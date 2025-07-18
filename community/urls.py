from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'branches', views.BranchViewSet)
router.register(r'members', views.MemberViewSet)
router.register(r'announcements', views.AnnouncementViewSet)
router.register(r'events', views.EventViewSet)
router.register(r'payments', views.MemberPaymentViewSet)
router.register(r'deposits', views.DepositViewSet)
router.register(r'member-deposits', views.MemberDepositViewSet)
router.register(r'loans', views.LoanViewSet)
router.register(r'member-loans', views.MemberLoanViewSet)
router.register(r'documents', views.DocumentViewSet)
router.register(r'minutes', views.MinuteViewSet)
router.register(r'feedback', views.FeedbackViewSet)
router.register(r'messages', views.MessageViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api/', include(router.urls)),
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
    # You might want to add a login/logout endpoint here for session authentication
    # For token authentication, you'd typically use rest_framework.authtoken.views.obtain_auth_token
    #path('auth/token/', include('rest_framework.authtoken.urls')), # For obtaining auth tokens
]