from django.contrib.auth.models import User
from rest_framework import serializers
from .models import (
    Branch, Member, MemberMetadata, MemberFinances, Announcement, Event,
    MemberPayment, Deposit, MemberDeposit, DepositPayment, Loan, MemberLoan,
    LoanRefund, Document, Minute, Feedback, Message
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'is_active']
        read_only_fields = ['id']


class BranchSerializer(serializers.ModelSerializer):
    child_branches = serializers.SerializerMethodField()

    class Meta:
        model = Branch
        fields = ['branch_id', 'branch_name', 'contact_email', 'branch_parent',
                  'branch_logo', 'created_at', 'child_branches']
        read_only_fields = ['branch_id', 'created_at']

    def get_child_branches(self, obj):
        return BranchSerializer(obj.child_branches.all(), many=True).data


class MemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Member
        fields = ['id', 'branch', 'user', 'user_id', 'phone_number', 'birthday',
                  'parent', 'spouse', 'status', 'bio', 'profile_pic']
        read_only_fields = ['id']


class MemberMetadataSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberMetadata
        fields = ['id', 'user', 'login_time', 'login_location']
        read_only_fields = ['id', 'login_time']


class MemberFinancesSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberFinances
        fields = ['user', 'total_savings', 'total_loans', 'last_updated_by', 'last_updated_at']
        read_only_fields = ['last_updated_at']


class AnnouncementSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    updated_by = UserSerializer(read_only=True)

    class Meta:
        model = Announcement
        fields = ['announcement_id', 'title', 'content', 'branch', 'start_date',
                  'end_date', 'created_by', 'created_at', 'updated_by', 'updated_at']
        read_only_fields = ['announcement_id', 'created_at', 'updated_at']


class EventSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    updated_by = UserSerializer(read_only=True)

    class Meta:
        model = Event
        fields = ['event_id', 'branch', 'title', 'description', 'start_time',
                  'end_time', 'created_by', 'created_at', 'updated_by', 'updated_at']
        read_only_fields = ['event_id', 'created_at', 'updated_at']


class MemberPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberPayment
        fields = ['payment_id', 'user', 'payment_amount', 'payment_date',
                  'created_by', 'created_at']
        read_only_fields = ['payment_id', 'created_at']


class DepositSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deposit
        fields = ['deposit_id', 'branch', 'name', 'min_amount', 'is_active',
                  'created_at', 'updated_by', 'updated_at']
        read_only_fields = ['deposit_id', 'created_at', 'updated_at']


class MemberDepositSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberDeposit
        fields = ['id', 'member', 'deposit', 'total_deposit_amount', 'interest_earned',
                  'accrued_principal', 'created_by', 'created_at']
        read_only_fields = ['id', 'created_at']


class DepositPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepositPayment
        fields = ['payment_id', 'deposit', 'deposit_amount', 'previous_balance', 'new_balance']
        read_only_fields = ['payment_id']


class LoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = ['loan_id', 'loan_name', 'loan_branch', 'interest_rate',
                  'is_active', 'status', 'updated_by', 'updated_at']
        read_only_fields = ['loan_id', 'updated_at']


class MemberLoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberLoan
        fields = ['id', 'user', 'loan', 'loan_amount', 'disbursement_date',
                  'interest_amount', 'interest_paid', 'principal_paid',
                  'accrued_principal', 'created_by', 'created_at']
        read_only_fields = ['id', 'created_at']


class LoanRefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanRefund
        fields = ['payment_id', 'deposit', 'deposit_amount', 'previous_balance', 'new_balance']
        read_only_fields = ['payment_id']


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['doc_id', 'branch', 'file_name', 'file_type', 'uploaded_by',
                  'uploaded_at', 'doc_content']
        read_only_fields = ['doc_id', 'uploaded_at']


class MinuteSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    adopter1 = UserSerializer(read_only=True)
    adopter2 = UserSerializer(read_only=True)

    class Meta:
        model = Minute
        fields = ['id', 'meeting_date', 'adopted', 'content', 'venue',
                  'created_by', 'adopter1', 'adopter2', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class FeedbackSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = Feedback
        fields = ['feedback_id', 'feedback_content', 'created_by', 'created_at']
        read_only_fields = ['feedback_id', 'created_at']


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'sender', 'receiver', 'subject', 'content',
                  'created_at', 'read_status']
        read_only_fields = ['id', 'created_at']
