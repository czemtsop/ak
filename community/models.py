from django.contrib.auth.models import User
from django.db import models


class Branch(models.Model):
    branch_id = models.AutoField(primary_key=True)
    branch_name = models.CharField(max_length=255)
    contact_email = models.EmailField(null=True, blank=True)
    branch_parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='child_branches')
    branch_logo = models.ImageField(upload_to='branch_logos/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Branches"

    def __str__(self):
        return self.branch_name


class Member(models.Model):
    """
    Extends Django's built-in User model to add additional profile information.
    OneToOneField ensures each User has one Profile and vice-versa.
    """
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    birthday = models.DateField(null=True, blank=True)
    parent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,  related_name='children')
    spouse = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='partner')
    status = models.CharField(max_length=50, default='active')
    bio = models.TextField(blank=True, null=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} ({self.user.first_name} {self.user.last_name})"


class MemberMetadata(models.Model):
    user = models.ForeignKey(Member, on_delete=models.CASCADE)
    login_time = models.DateTimeField(auto_now_add=True)
    login_location = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.login_time}"


class MemberFinances(models.Model):
    user = models.OneToOneField(Member, on_delete=models.CASCADE, primary_key=True)
    total_savings = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_loans = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    last_updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='updated_finances')
    last_updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - Savings: {self.total_savings}, Loans: {self.total_loans}"


class Announcement(models.Model):
    """
    Model for general announcements. Only admins can create, edit, or delete these.
    """
    announcement_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    content = models.TextField()
    branch = models.ForeignKey(Branch, default=0, on_delete=models.CASCADE, related_name='branch_news')
    start_date = models.DateField()
    end_date = models.DateField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='announcements_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='announcements_updated')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date'] # Order announcements by most recent first

    def __str__(self):
        return self.title

class Event(models.Model):
    """
    Model for community events. Only admins can create, edit, or delete these.
    """
    event_id = models.AutoField(primary_key=True)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='branch_events')
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='events_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='events_updated')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Event {self.title} - {self.branch.branch_name}"
    class Meta:
        ordering = ['-start_time'] # Order announcements by most recent first


class MemberPayment(models.Model):
    payment_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Member, on_delete=models.CASCADE)
    payment_amount = models.DecimalField(max_digits=15, decimal_places=2)
    payment_date = models.DateField()
    created_by = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='created_payments')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.user.username} - {self.payment_id}"


class Deposit(models.Model):
    deposit_id = models.AutoField(primary_key=True)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    min_amount = models.IntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class MemberDeposit(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    deposit = models.ForeignKey(Deposit, on_delete=models.CASCADE)
    total_deposit_amount = models.DecimalField(max_digits=15, decimal_places=2)
    interest_earned = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    accrued_principal = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    created_by = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='created_member_deposits')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('member', 'deposit')

    def __str__(self):
        return f"{self.member.username} - {self.deposit.deposit_name}"


class DepositPayment(models.Model):
    payment_id = models.AutoField(primary_key=True)
    deposit = models.ForeignKey(Deposit, on_delete=models.CASCADE)
    deposit_amount = models.DecimalField(max_digits=15, decimal_places=2)
    previous_balance = models.DecimalField(max_digits=15, decimal_places=2)
    new_balance = models.DecimalField(max_digits=15, decimal_places=2)

    def __str__(self):
        return f"Payment {self.payment_id} - {self.deposit.deposit_name}"


class Loan(models.Model):
    loan_id = models.AutoField(primary_key=True)
    loan_name = models.CharField(max_length=200)
    loan_branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    interest_rate = models.FloatField()
    is_active = models.BooleanField(default=True)
    status = models.CharField(max_length=100)  # e.g. active, closed, default
    updated_by = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.loan_name


class MemberLoan(models.Model):
    user = models.ForeignKey(Member, on_delete=models.CASCADE)
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE)
    loan_amount = models.DecimalField(max_digits=15, decimal_places=2)
    disbursement_date = models.DateField()
    interest_amount = models.DecimalField(max_digits=15, decimal_places=2)
    interest_paid = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    principal_paid = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    accrued_principal = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    created_by = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='created_member_loans')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'loan')

    def __str__(self):
        return f"{self.user.username} - {self.loan.loan_name}"


class LoanRefund(models.Model):
    payment_id = models.AutoField(primary_key=True)
    deposit = models.ForeignKey(Deposit, on_delete=models.CASCADE)
    deposit_amount = models.DecimalField(max_digits=15, decimal_places=2)
    previous_balance = models.DecimalField(max_digits=15, decimal_places=2)
    new_balance = models.DecimalField(max_digits=15, decimal_places=2)

    def __str__(self):
        return f"Refund {self.payment_id}"


class Document(models.Model):
    doc_id = models.AutoField(primary_key=True)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    file_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=100)
    uploaded_by = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='uploaded_documents')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    doc_content = models.FileField(upload_to='documents/')

    def __str__(self):
        return f"{self.file_name} - {self.branch}"


class Minute(models.Model):
    """
    Model for meeting minutes. Only admins can create, edit, or delete these.
    """
    meeting_date = models.DateField()
    adopted = models.BooleanField()
    content = models.TextField()
    venue = models.CharField(max_length=200, unique_for_month="meeting_date")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='minutes_created')
    adopter1 = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='minutes_adopted')
    adopter2 = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='minutes_adopted2')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at'] # Order announcements by most recent first

    def __str__(self):
        return self.venue


class Feedback(models.Model):
    feedback_id = models.AutoField(primary_key=True)
    feedback_content = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback {self.feedback_id} by {self.created_by.username}"


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
