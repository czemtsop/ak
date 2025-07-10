from django.contrib.auth.models import User
from rest_framework import viewsets, mixins, status
from django.http import HttpResponse
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from . import models
from .models import Announcement, Message
from .permissions import IsAdminUser, IsOwnerOrAdminForMessage
from .serializers import UserSerializer, AnnouncementSerializer, MessageSerializer


class UserViewSet(mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  mixins.UpdateModelMixin, # For updating profile
                  viewsets.GenericViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    - Members can list all other members.
    - Members can retrieve their own profile.
    - Members can update their own profile.
    - Admins can manage user accounts (add, deactivate - though 'add' is not explicitly here,
      it's usually done via Django Admin or a separate registration endpoint).
      For simplicity, deactivation can be done by admin setting `is_active` to False.
    """
    queryset = User.objects.filter(is_active=True).order_by('username') # Only show active users
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['username', 'first_name', 'last_name', 'email'] # Enable search for members

    def get_queryset(self):
        """
        Allow admins to see all users (including inactive for management),
        but members only see active users.
        """
        if self.request.user.is_staff:
            return User.objects.all().order_by('username')
        return super().get_queryset()

    def get_object(self):
        """
        Allow authenticated users to retrieve their own profile using '/users/me/'.
        Otherwise, use the default lookup for other users.
        """
        if self.action == 'me':
            return self.request.user
        return super().get_object()

    @action(detail=False, methods=['get', 'put'], url_path='me')
    def me(self, request):
        """
        Endpoint for authenticated user to view and update their own profile.
        """
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = self.get_serializer(request.user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


class AnnouncementViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows announcements to be viewed, created, edited or deleted.
    - Members can see general announcements (GET).
    - Admins can create, edit, and delete general announcements (POST, PUT/PATCH, DELETE).
    """
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
    permission_classes = [IsAuthenticated, IsAdminUser] # Requires authentication and admin status for write ops

    def perform_create(self, serializer):
        """
        Set the created_by field to the current authenticated user.
        """
        serializer.save(created_by=self.request.user)

class MessageViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows messages to be viewed, created, edited or deleted.
    - Members can receive and view specific messages sent directly to them.
    - Admins can view all specific messages.
    """
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdminForMessage]

    def get_queryset(self):
        """
        Filter messages to only show those sent to or by the current user,
        or all messages if the user is an admin.
        """
        user = self.request.user
        if user.is_staff: # Admin can view all messages
            return Message.objects.all().order_by('-created_at')
        # Members can only see messages where they are sender or receiver
        return Message.objects.filter(models.Q(sender=user) | models.Q(receiver=user)).order_by('-created_at')

    def perform_create(self, serializer):
        """
        Set the sender of the message to the current authenticated user.
        The receiver is handled by the serializer's create method.
        """
        serializer.save(sender=self.request.user)

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """
        Action to mark a specific message as read.
        Only the receiver of the message can mark it as read.
        """
        message = self.get_object()
        if request.user == message.receiver:
            message.read_status = True
            message.save()
            return Response({'status': 'message marked as read'})
        return Response({'detail': 'You are not authorized to mark this message as read.'}, status=status.HTTP_403_FORBIDDEN)
