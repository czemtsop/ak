from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    """
    Extends Django's built-in User model to add additional profile information.
    OneToOneField ensures each User has one Profile and vice-versa.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=15, blank=True, null=True)
    birthday = models.DateField(blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='children')
    spouse = models.OneToOneField('self', on_delete=models.CASCADE, blank=True, null=True, related_name='partner')
    total_savings = models.IntegerField(default=0, editable=False)
    total_loans = models.IntegerField(default=0, editable=False)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} ({self.user.first_name} {self.user.last_name})"


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

class Minute(models.Model):
    """
    Model for meeting minutes. Only admins can create, edit, or delete these.
    """
    venue = models.CharField(max_length=200, unique_for_month="meeting_date")
    meeting_date = models.DateField()
    adopted = models.BooleanField()
    content = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='minutes_created')
    adopter1 = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='minutes_adopted')
    adopter2 = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='minutes_adopted2')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at'] # Order announcements by most recent first

    def __str__(self):
        return self.venue

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

