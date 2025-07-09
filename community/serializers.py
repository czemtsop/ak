from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, Announcement, Message

class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for the Profile model.
    """
    class Meta:
        model = Profile
        fields = ['bio'] # Add other profile fields here if you expand the Profile model

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model, including nested Profile.
    Used for listing members and updating user profiles.
    """
    profile = ProfileSerializer(required=False) # Nested serializer for Profile

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile']
        read_only_fields = ['username'] # Username usually shouldn't be changed after creation

    def update(self, instance, validated_data):
        """
        Custom update method to handle nested Profile data.
        """
        profile_data = validated_data.pop('profile', {})
        instance = super().update(instance, validated_data)

        # Update or create profile
        profile, created = Profile.objects.get_or_create(user=instance)
        for attr, value in profile_data.items():
            setattr(profile, attr, value)
        profile.save()

        return instance


class AnnouncementSerializer(serializers.ModelSerializer):
    """
    Serializer for the Announcement model.
    """
    created_by = serializers.ReadOnlyField(source='created_by.username') # Display username of creator

    class Meta:
        model = Announcement
        fields = ['id', 'title', 'content', 'created_by', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at', 'created_by'] # These fields are set automatically

class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for the Message model.
    Handles creation, viewing, and updating (e.g., read_status).
    """
    sender = serializers.ReadOnlyField(source='sender.username') # Display username of sender
    receiver_username = serializers.CharField(write_only=True, required=True) # Field for receiving receiver's username

    class Meta:
        model = Message
        fields = ['id', 'sender', 'receiver', 'receiver_username', 'subject', 'content', 'created_at', 'read_status']
        read_only_fields = ['created_at', 'sender', 'receiver'] # Sender and receiver set by view

    def create(self, validated_data):
        """
        Custom create method to set the receiver based on username.
        """
        receiver_username = validated_data.pop('receiver_username')
        try:
            receiver = User.objects.get(username=receiver_username)
        except User.DoesNotExist:
            raise serializers.ValidationError({"receiver_username": "User with this username does not exist."})

        validated_data['receiver'] = receiver
        validated_data['sender'] = self.context['request'].user # Set sender to the current authenticated user
        return super().create(validated_data)

    def to_representation(self, instance):
        """
        Override to_representation to display receiver's username in read operations.
        """
        ret = super().to_representation(instance)
        ret['receiver'] = instance.receiver.username # Replace receiver ID with username for display
        return ret
