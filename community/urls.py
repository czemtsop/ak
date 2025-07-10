from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import UserViewSet, AnnouncementViewSet, MessageViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'announcements', AnnouncementViewSet, basename='announcement')
router.register(r'messages', MessageViewSet, basename='message')

urlpatterns = [
    path('', include(router.urls)),
    # You might want to add a login/logout endpoint here for session authentication
    # For token authentication, you'd typically use rest_framework.authtoken.views.obtain_auth_token
    path('auth/', include('rest_framework.urls', namespace='rest_framework')), # For browsable API login/logout
    #path('auth/token/', include('rest_framework.authtoken.urls')), # For obtaining auth tokens
]