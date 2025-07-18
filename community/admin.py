from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import (
    Branch, Member, MemberFinances, Announcement, Event,
    MemberPayment, Deposit, MemberDeposit, DepositPayment, Loan, MemberLoan,
    LoanRefund, Document, Minute, Feedback, Message
)
from .webhooks import WebhookEndpoint

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ['branch_name', 'contact_email', 'parent_branch_name', 'created_at']
    list_filter = ['created_at', 'branch_parent']
    search_fields = ['branch_name', 'contact_email']
    readonly_fields = ['created_at']
    fields = ['branch_name', 'contact_email', 'branch_parent', 'branch_logo', 'created_at']

    def parent_branch_name(self, obj):
        return obj.branch_parent.branch_name if obj.branch_parent else "Root Branch"
    parent_branch_name.short_description = "Parent Branch"

# Define an inline admin descriptor for Member model
# which acts a bit like a singleton
# class MemberInline(admin.StackedInline):
#     model = Member
#     can_delete = False
#     verbose_name_plural = 'profile'
#     fk_name = 'profile'


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    #inlines = (MemberInline,)
    #list_display = ['user__username', 'branch', 'phone_number', 'birthday', 'status']
    #list_filter = ['is_staff', 'user__is_active', 'branch', 'status', 'birthday']
    search_fields = ['username', 'first_name', 'last_name', 'branch_name', 'phone_number']
    ordering = ('user__username',)
    fieldsets = (
        (None, {
            'fields': ('username', 'branch', 'phone_number', 'birthday', 'status')
        }),
        ('Relationships', {
            'fields': ('parent', 'spouse'),
        }),
        ('Additional Info', {
            'fields': ('bio', 'profile_pic'),
        }),
    )

    def user_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}" if obj.user.first_name else obj.user.username
    user_full_name.short_description = "Full Name"

    def username(self, obj):
        return obj.user.username
    username.short_description = "Username"


@admin.register(MemberFinances)
class MemberFinancesAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_savings', 'total_loans', 'last_updated_by', 'last_updated_at']
    list_filter = ['last_updated_at']
    search_fields = ['user__user__username']
    readonly_fields = ['last_updated_at', 'total_savings', 'total_loans', 'last_updated_by']

    def save_model(self, request, obj, form, change):
        obj.last_updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(MemberPayment)
class MemberPaymentAdmin(admin.ModelAdmin):
    list_display = ['payment_id', 'user', 'payment_amount', 'payment_date', 'created_by']
    list_filter = ['payment_date', 'created_at']
    search_fields = ['user__user__username', 'payment_id']
    readonly_fields = ['created_at']
    date_hierarchy = 'payment_date'

    def save_model(self, request, obj, form, change):
        if not change:  # New object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Deposit)
class DepositAdmin(admin.ModelAdmin):
    list_display = ['name', 'branch', 'min_amount', 'is_active', 'updated_by', 'updated_at']
    list_filter = ['is_active', 'branch', 'updated_at']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(MemberDeposit)
class MemberDepositAdmin(admin.ModelAdmin):
    list_display = ['member', 'deposit', 'total_deposit_amount', 'interest_earned', 'created_at']
    list_filter = ['deposit', 'created_at']
    search_fields = ['member__user__username', 'deposit__name']
    readonly_fields = ['created_at']

    def save_model(self, request, obj, form, change):
        if not change:  # New object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(DepositPayment)
class DepositPaymentAdmin(admin.ModelAdmin):
    list_display = ['payment_id', 'deposit', 'deposit_amount', 'previous_balance', 'new_balance']
    list_filter = ['deposit']
    search_fields = ['deposit__name']


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ['loan_name', 'loan_branch', 'interest_rate', 'is_active', 'status', 'updated_at']
    list_filter = ['is_active', 'status', 'loan_branch', 'updated_at']
    search_fields = ['loan_name']
    readonly_fields = ['updated_at']

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(MemberLoan)
class MemberLoanAdmin(admin.ModelAdmin):
    list_display = ['user', 'loan', 'loan_amount', 'disbursement_date', 'interest_amount', 'balance_remaining']
    list_filter = ['loan', 'disbursement_date', 'created_at']
    search_fields = ['user__user__username', 'loan__loan_name']
    readonly_fields = ['created_at']
    date_hierarchy = 'disbursement_date'

    def balance_remaining(self, obj):
        return obj.loan_amount + obj.interest_amount - obj.principal_paid - obj.interest_paid

    balance_remaining.short_description = "Balance Remaining"

    def save_model(self, request, obj, form, change):
        if not change:  # New object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(LoanRefund)
class LoanRefundAdmin(admin.ModelAdmin):
    list_display = ['payment_id', 'deposit', 'deposit_amount', 'previous_balance', 'new_balance']
    list_filter = ['deposit']
    search_fields = ['deposit__name']


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['file_name', 'file_type', 'branch', 'uploaded_by', 'uploaded_at']
    list_filter = ['file_type', 'branch', 'uploaded_at']
    search_fields = ['file_name', 'uploaded_by__user__username']
    readonly_fields = ['uploaded_at']
    date_hierarchy = 'uploaded_at'


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'branch', 'start_date', 'end_date', 'created_by', 'created_at']
    list_filter = ['branch', 'start_date', 'end_date', 'created_at']
    search_fields = ['title', 'content']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'start_date'

    fields = [
        'title', 'content', 'branch', 'start_date', 'end_date',
        'created_by', 'created_at', 'updated_by', 'updated_at'
    ]

    def save_model(self, request, obj, form, change):
        if not change:  # New object
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Minute)
class MinuteAdmin(admin.ModelAdmin):
    list_display = ['venue', 'meeting_date', 'adopted', 'created_by', 'adopter1', 'adopter2']
    list_filter = ['adopted', 'meeting_date', 'created_at']
    search_fields = ['venue', 'content']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'meeting_date'

    fields = [
        'venue', 'meeting_date', 'content', 'adopted', 'created_by',
        'adopter1', 'adopter2', 'created_at', 'updated_at'
    ]

    def save_model(self, request, obj, form, change):
        if not change:  # New object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['feedback_id', 'created_by', 'created_at', 'feedback_preview']
    list_filter = ['created_at', 'created_by__username']
    search_fields = ['feedback_content', 'created_by__username']
    readonly_fields = ['created_at', 'created_by', 'feedback_content']
    date_hierarchy = 'created_at'

    def feedback_preview(self, obj):
        return obj.feedback_content[:100] + "..." if len(obj.feedback_content) > 100 else obj.feedback_content
    feedback_preview.short_description = "Preview"


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("branch", "title", "description", "start_time", "end_time")
    list_filter = ("branch", 'end_time')
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'start_time'

    fields = [
        'title', 'description', 'branch', 'start_time', 'end_time'
    ]

    def save_model(self, request, obj, form, change):
        if not change:  # New object
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, MemberAdmin)

# Register other models
admin.site.register(Message)
admin.site.register(WebhookEndpoint)

# Customize the admin site header and title
admin.site.site_header = "Community Admin Console"
admin.site.site_title = "MMS Admin"
admin.site.index_title = "Welcome to the Admin Console"
