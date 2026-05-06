from django.db import models
from django.conf import settings
from django.utils import timezone


class Notification(models.Model):
    TYPE_APPROVAL = 'approval'
    TYPE_REJECTION = 'rejection'
    TYPE_PAYMENT = 'payment'
    TYPE_DISBURSEMENT = 'disbursement'
    TYPE_REPAYMENT = 'repayment'
    TYPE_INFO = 'info'

    TYPE_CHOICES = [
        (TYPE_APPROVAL, 'Loan Approved'),
        (TYPE_REJECTION, 'Loan Rejected'),
        (TYPE_PAYMENT, 'Payment Confirmed'),
        (TYPE_DISBURSEMENT, 'Loan Disbursed'),
        (TYPE_REPAYMENT, 'Repayment Received'),
        (TYPE_INFO, 'Information'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications'
    )
    loan = models.ForeignKey(
        'loans.LoanApplication', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='notifications'
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_INFO)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.notification_type}] {self.title} → {self.user.email}"

    def get_icon(self):
        icons = {
            self.TYPE_APPROVAL: 'fas fa-check-circle text-success',
            self.TYPE_REJECTION: 'fas fa-times-circle text-danger',
            self.TYPE_PAYMENT: 'fas fa-credit-card text-primary',
            self.TYPE_DISBURSEMENT: 'fas fa-money-bill-wave text-success',
            self.TYPE_REPAYMENT: 'fas fa-undo text-info',
            self.TYPE_INFO: 'fas fa-info-circle text-warning',
        }
        return icons.get(self.notification_type, 'fas fa-bell')
