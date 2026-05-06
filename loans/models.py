from django.db import models
from django.conf import settings
from django.utils import timezone


class LoanApplication(models.Model):
    AMOUNT_CHOICES = [(a, f"KES {a:,}") for a in [3000, 5000, 10000, 20000]]

    STATUS_PENDING = 'pending'
    STATUS_UNDER_REVIEW = 'under_review'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    STATUS_DEPOSIT_PENDING = 'deposit_pending'
    STATUS_DEPOSIT_PAID = 'deposit_paid'
    STATUS_DISBURSED = 'disbursed'
    STATUS_REPAID = 'repaid'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending Review'),
        (STATUS_UNDER_REVIEW, 'Under Review'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
        (STATUS_DEPOSIT_PENDING, 'Awaiting Deposit'),
        (STATUS_DEPOSIT_PAID, 'Deposit Paid - Awaiting Disbursement'),
        (STATUS_DISBURSED, 'Disbursed'),
        (STATUS_REPAID, 'Repaid'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='loan_applications'
    )
    qualified_amount = models.IntegerField(choices=AMOUNT_CHOICES)
    requested_amount = models.IntegerField(choices=AMOUNT_CHOICES)
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    reason = models.TextField()
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default=STATUS_PENDING)
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    disbursed_at = models.DateTimeField(null=True, blank=True)
    repaid_at = models.DateTimeField(null=True, blank=True)
    admin_notes = models.TextField(blank=True)
    rejection_reason = models.TextField(blank=True)
    repayment_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    repayment_reference = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"Loan #{self.pk} - {self.user.email} - KES {self.requested_amount:,} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        if not self.deposit_amount and self.requested_amount:
            pct = getattr(settings, 'DEPOSIT_PERCENTAGE', 10)
            self.deposit_amount = (self.requested_amount * pct) / 100
        super().save(*args, **kwargs)

    def get_status_badge(self):
        badges = {
            self.STATUS_PENDING: 'warning',
            self.STATUS_UNDER_REVIEW: 'info',
            self.STATUS_APPROVED: 'success',
            self.STATUS_REJECTED: 'danger',
            self.STATUS_DEPOSIT_PENDING: 'warning',
            self.STATUS_DEPOSIT_PAID: 'primary',
            self.STATUS_DISBURSED: 'success',
            self.STATUS_REPAID: 'secondary',
        }
        return badges.get(self.status, 'secondary')

    def get_progress_percentage(self):
        steps = [
            self.STATUS_PENDING,
            self.STATUS_UNDER_REVIEW,
            self.STATUS_APPROVED,
            self.STATUS_DEPOSIT_PENDING,
            self.STATUS_DEPOSIT_PAID,
            self.STATUS_DISBURSED,
        ]
        try:
            idx = steps.index(self.status)
            return int(((idx + 1) / len(steps)) * 100)
        except ValueError:
            return 100 if self.status == self.STATUS_REPAID else 0
