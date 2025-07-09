from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    """
    Custom permission to only allow admin users (is_staff=True) to access.
    """
    def has_permission(self, request, view):
        # Read permissions are allowed to any authenticated user,
        # so we'll only check for write permissions.
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        # Write permissions are only allowed to admin users.
        return request.user and request.user.is_authenticated and request.user.is_staff

class IsOwnerOrAdminForMessage(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object (sender/receiver of message)
    or admin users to view/edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to sender, receiver, or admin.
        if request.method in permissions.SAFE_METHODS:
            return (obj.sender == request.user or
                    obj.receiver == request.user or
                    request.user.is_staff)
        # Write permissions are only allowed to the sender or admin.
        # For messages, usually only sender can edit/delete, or admin.
        # For simplicity, we'll allow sender to delete/update.
        return (obj.sender == request.user or request.user.is_staff)
