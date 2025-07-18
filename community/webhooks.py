import json
import requests
from django.conf import settings
from django.core.serializers import serialize
from django.db import models
from typing import Any, Dict, List
import logging

logger = logging.getLogger(__name__)


class WebhookEndpoint(models.Model):
    """Model to store webhook endpoints"""
    url = models.URLField()
    event_types = models.JSONField(default=list)  # List of event types to subscribe to
    is_active = models.BooleanField(default=True)
    secret = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.url} - {self.event_types}"


class WebhookLog(models.Model):
    """Model to log webhook delivery attempts"""
    endpoint = models.ForeignKey(WebhookEndpoint, on_delete=models.CASCADE)
    event_type = models.CharField(max_length=100)
    payload = models.JSONField()
    status_code = models.IntegerField(null=True)
    response_body = models.TextField(blank=True)
    success = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.endpoint.url} - {self.event_type} - {'Success' if self.success else 'Failed'}"


class WebhookManager:
    """Manager class for handling webhook operations"""

    @staticmethod
    def trigger_webhook(event_type: str, instance: Any, extra_data: Dict = None):
        """
        Trigger webhooks for a specific event type

        Args:
            event_type: Type of event (e.g., 'member.created', 'payment.created')
            instance: The model instance that triggered the event
            extra_data: Additional data to include in the payload
        """
        # Get all active endpoints subscribed to this event type
        endpoints = WebhookEndpoint.objects.filter(
            is_active=True,
            event_types__contains=[event_type]
        )

        for endpoint in endpoints:
            WebhookManager._send_webhook(endpoint, event_type, instance, extra_data)

    @staticmethod
    def _send_webhook(endpoint: WebhookEndpoint, event_type: str, instance: Any, extra_data: Dict = None):
        """
        Send webhook to a specific endpoint

        Args:
            endpoint: WebhookEndpoint instance
            event_type: Type of event
            instance: The model instance
            extra_data: Additional data
        """
        # Prepare payload
        payload = {
            'event_type': event_type,
            'timestamp': instance.created_at.isoformat() if hasattr(instance, 'created_at') else None,
            'data': WebhookManager._serialize_instance(instance)
        }

        if extra_data:
            payload.update(extra_data)

        # Create webhook log entry
        log_entry = WebhookLog.objects.create(
            endpoint=endpoint,
            event_type=event_type,
            payload=payload
        )

        try:
            # Prepare headers
            headers = {
                'Content-Type': 'application/json',
                'X-Event-Type': event_type,
            }

            if endpoint.secret:
                import hmac
                import hashlib
                signature = hmac.new(
                    endpoint.secret.encode('utf-8'),
                    json.dumps(payload).encode('utf-8'),
                    hashlib.sha256
                ).hexdigest()
                headers['X-Webhook-Signature'] = f'sha256={signature}'

            # Send webhook
            response = requests.post(
                endpoint.url,
                json=payload,
                headers=headers,
                timeout=30
            )

            # Update log entry
            log_entry.status_code = response.status_code
            log_entry.response_body = response.text
            log_entry.success = response.status_code < 400
            log_entry.attempts = 1
            log_entry.save()

            logger.info(f"Webhook sent successfully to {endpoint.url} for {event_type}")

        except Exception as e:
            # Update log entry with error
            log_entry.success = False
            log_entry.attempts = 1
            log_entry.response_body = str(e)
            log_entry.save()

            logger.error(f"Failed to send webhook to {endpoint.url} for {event_type}: {str(e)}")

    @staticmethod
    def _serialize_instance(instance: Any) -> Dict:
        """
        Serialize model instance to dictionary

        Args:
            instance: Model instance to serialize

        Returns:
            Dictionary representation of the instance
        """
        # Get all fields from the model
        data = {}

        for field in instance._meta.fields:
            value = getattr(instance, field.name)

            # Handle different field types
            if isinstance(field, models.DateTimeField) and value:
                data[field.name] = value.isoformat()
            elif isinstance(field, models.DateField) and value:
                data[field.name] = value.isoformat()
            elif isinstance(field, models.ForeignKey) and value:
                data[field.name] = value.pk
                # Add related object info
                if hasattr(value, '__str__'):
                    data[f"{field.name}_display"] = str(value)
            elif isinstance(field, models.FileField) and value:
                data[field.name] = value.url if value else None
            elif isinstance(field, models.ImageField) and value:
                data[field.name] = value.url if value else None
            else:
                data[field.name] = value

        return data