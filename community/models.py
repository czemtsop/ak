from django.db import models

from django.contrib.auth.models import User
from django.conf import settings # Import settings to get AUTH_USER_MODEL if custom user model is used

class Profile(models.Model):
    """
    Extends Django's built-in User model to add additional profile information.
    OneToOneField ensures each User has one Profile and vice-versa.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    # Add other profile fields here as needed, e.g., phone_number, address, etc.
    # For now, we'll keep it simple as the user story only mentions "name, contact details"
    # which are largely covered by the User model or can be implicitly handled.
    # We'll just add a placeholder for future expansion.
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Profile for {self.user.username}"

class Announcement(models.Model):
    """
    Model for general announcements. Only admins can create, edit, or delete these.
    """
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='announcements_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at'] # Order announcements by most recent first

    def __str__(self):
        return self.title

class Message(models.Model):
    """
    Model for specific messages sent between members.
    """
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    subject = models.CharField(max_length=255, blank=True, null=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read_status = models.BooleanField(default=False) # True if the receiver has read the message

    class Meta:
        ordering = ['-created_at'] # Order messages by most recent first

    def __str__(self):
        return f"From {self.sender.username} to {self.receiver.username}: {self.subject or self.content[:50]}"

