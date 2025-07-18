from django.contrib import admin
from .webhooks import WebhookEndpoint, WebhookLog


@admin.register(WebhookEndpoint)
class WebhookEndpointAdmin(admin.ModelAdmin):
    list_display = ['url', 'is_active', 'event_types', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['url']
    readonly_fields = ['created_at']


@admin.register(WebhookLog)
class WebhookLogAdmin(admin.ModelAdmin):
    list_display = ['endpoint', 'event_type', 'success', 'status_code', 'attempts', 'created_at']
    list_filter = ['success', 'event_type', 'created_at']
    search_fields = ['endpoint__url', 'event_type']
    readonly_fields = ['created_at']

    def has_add_permission(self, request):
        return False  # Prevent manual creation of log entries