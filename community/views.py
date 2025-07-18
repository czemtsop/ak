from django.contrib.auth.models import User
from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, status, mixins, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import *
from .serializers import *
from .webhooks import WebhookManager
from . import models
from .models import Announcement, Message
from .permissions import IsAdminUser, IsOwnerOrAdminForMessage
from .serializers import UserSerializer, AnnouncementSerializer, MessageSerializer


class BranchViewSet(viewsets.ModelViewSet):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        instance = serializer.save()
        WebhookManager.trigger_webhook('branch.created', instance)

    def perform_update(self, serializer):
        instance = serializer.save()
        WebhookManager.trigger_webhook('branch.updated', instance)

    def perform_destroy(self, instance):
        WebhookManager.trigger_webhook('branch.deleted', instance)
        instance.delete()


class MemberViewSet(viewsets.ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        instance = serializer.save()
        WebhookManager.trigger_webhook('member.created', instance)

    def perform_update(self, serializer):
        instance = serializer.save()
        WebhookManager.trigger_webhook('member.updated', instance)

    @action(detail=True, methods=['get'])
    def finances(self, request, pk=None):
        member = self.get_object()
        try:
            finances = MemberFinances.objects.get(user=member)
            serializer = MemberFinancesSerializer(finances)
            return Response(serializer.data)
        except MemberFinances.DoesNotExist:
            return Response({'error': 'Finances not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'])
    def loans(self, request, pk=None):
        member = self.get_object()
        loans = MemberLoan.objects.filter(user=member)
        serializer = MemberLoanSerializer(loans, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def deposits(self, request, pk=None):
        member = self.get_object()
        deposits = MemberDeposit.objects.filter(member=member)
        serializer = MemberDepositSerializer(deposits, many=True)
        return Response(serializer.data)


class AnnouncementViewSet(viewsets.ModelViewSet):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        instance = serializer.save(created_by=self.request.user)
        WebhookManager.trigger_webhook('announcement.created', instance)

    def perform_update(self, serializer):
        instance = serializer.save(updated_by=self.request.user)
        WebhookManager.trigger_webhook('announcement.updated', instance)

    def get_queryset(self):
        queryset = Announcement.objects.all()
        branch = self.request.query_params.get('branch', None)
        if branch is not None:
            queryset = queryset.filter(branch=branch)
        return queryset


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        instance = serializer.save(created_by=self.request.user)
        WebhookManager.trigger_webhook('event.created', instance)

    def perform_update(self, serializer):
        instance = serializer.save(updated_by=self.request.user)
        WebhookManager.trigger_webhook('event.updated', instance)

    def get_queryset(self):
        queryset = Event.objects.all()
        branch = self.request.query_params.get('branch', None)
        if branch is not None:
            queryset = queryset.filter(branch=branch)
        return queryset


class MemberPaymentViewSet(viewsets.ModelViewSet):
    queryset = MemberPayment.objects.all()
    serializer_class = MemberPaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        instance = serializer.save()
        WebhookManager.trigger_webhook('payment.created', instance)

    def get_queryset(self):
        queryset = MemberPayment.objects.all()
        user = self.request.query_params.get('user', None)
        if user is not None:
            queryset = queryset.filter(user=user)
        return queryset


class DepositViewSet(viewsets.ModelViewSet):
    queryset = Deposit.objects.all()
    serializer_class = DepositSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        instance = serializer.save()
        WebhookManager.trigger_webhook('deposit.created', instance)

    def perform_update(self, serializer):
        instance = serializer.save(updated_by=self.request.user)
        WebhookManager.trigger_webhook('deposit.updated', instance)


class MemberDepositViewSet(viewsets.ModelViewSet):
    queryset = MemberDeposit.objects.all()
    serializer_class = MemberDepositSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        instance = serializer.save()
        WebhookManager.trigger_webhook('member_deposit.created', instance)


class LoanViewSet(viewsets.ModelViewSet):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        instance = serializer.save()
        WebhookManager.trigger_webhook('loan.created', instance)

    def perform_update(self, serializer):
        instance = serializer.save(updated_by=self.request.user)
        WebhookManager.trigger_webhook('loan.updated', instance)


class MemberLoanViewSet(viewsets.ModelViewSet):
    queryset = MemberLoan.objects.all()
    serializer_class = MemberLoanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        instance = serializer.save()
        WebhookManager.trigger_webhook('member_loan.created', instance)


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        instance = serializer.save(uploaded_by=self.request.user)
        WebhookManager.trigger_webhook('document.uploaded', instance)


class MinuteViewSet(viewsets.ModelViewSet):
    queryset = Minute.objects.all()
    serializer_class = MinuteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        instance = serializer.save(created_by=self.request.user)
        WebhookManager.trigger_webhook('minute.created', instance)

    def perform_update(self, serializer):
        instance = serializer.save()
        WebhookManager.trigger_webhook('minute.updated', instance)


class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        instance = serializer.save(created_by=self.request.user)
        WebhookManager.trigger_webhook('feedback.created', instance)


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        instance = serializer.save(sender=self.request.user)
        WebhookManager.trigger_webhook('message.sent', instance)

    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(Q(sender=user) | Q(receiver=user))

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        message = self.get_object()
        if message.receiver == request.user:
            message.read_status = True
            message.save()
            WebhookManager.trigger_webhook('message.read', message)
            return Response({'status': 'message marked as read'})
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

