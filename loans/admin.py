from django.contrib import admin
from django.utils import timezone
from .models import LoanApplication
from notifications.models import Notification


@admin.register(LoanApplication)
class LoanApplicationAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'requested_amount', 'qualified_amount',
        'deposit_amount', 'status', 'submitted_at', 'approved_at'
    )
    list_filter = ('status', 'submitted_at', 'approved_at')
    search_fields = ('user__email', 'user__full_name', 'repayment_reference')
    readonly_fields = ('submitted_at', 'reviewed_at', 'approved_at', 'disbursed_at', 'repaid_at', 'deposit_amount')
    ordering = ('-submitted_at',)
    actions = ['approve_loans', 'reject_loans', 'mark_disbursed', 'mark_deposit_pending']

    fieldsets = (
        ('Applicant', {'fields': ('user',)}),
        ('Loan Details', {'fields': ('qualified_amount', 'requested_amount', 'deposit_amount', 'reason')}),
        ('Status', {'fields': ('status', 'admin_notes', 'rejection_reason')}),
        ('Repayment', {'fields': ('repayment_amount', 'repayment_reference')}),
        ('Timestamps', {'fields': ('submitted_at', 'reviewed_at', 'approved_at', 'disbursed_at', 'repaid_at')}),
    )

    def approve_loans(self, request, queryset):
        count = 0
        for loan in queryset.filter(status__in=[LoanApplication.STATUS_PENDING, LoanApplication.STATUS_UNDER_REVIEW]):
            loan.status = LoanApplication.STATUS_APPROVED
            loan.approved_at = timezone.now()
            loan.save()
            Notification.objects.create(
                user=loan.user,
                title="🎉 Loan Approved!",
                message=f"Your loan of KES {loan.requested_amount:,} has been approved. Please pay the deposit of KES {loan.deposit_amount:,.0f} to proceed.",
                notification_type=Notification.TYPE_APPROVAL,
                loan=loan,
            )
            count += 1
        self.message_user(request, f"{count} loan(s) approved.")
    approve_loans.short_description = "Approve selected loans"

    def reject_loans(self, request, queryset):
        count = queryset.exclude(status=LoanApplication.STATUS_REJECTED).update(status=LoanApplication.STATUS_REJECTED)
        self.message_user(request, f"{count} loan(s) rejected.")
    reject_loans.short_description = "Reject selected loans"

    def mark_disbursed(self, request, queryset):
        count = 0
        for loan in queryset.filter(status=LoanApplication.STATUS_DEPOSIT_PAID):
            loan.status = LoanApplication.STATUS_DISBURSED
            loan.disbursed_at = timezone.now()
            loan.save()
            Notification.objects.create(
                user=loan.user,
                title="💰 Loan Disbursed!",
                message=f"KES {loan.requested_amount:,} has been sent to your M-Pesa number. Please check your phone.",
                notification_type=Notification.TYPE_DISBURSEMENT,
                loan=loan,
            )
            count += 1
        self.message_user(request, f"{count} loan(s) marked as disbursed.")
    mark_disbursed.short_description = "Mark selected loans as disbursed"

    def mark_deposit_pending(self, request, queryset):
        count = queryset.filter(status=LoanApplication.STATUS_APPROVED).update(
            status=LoanApplication.STATUS_DEPOSIT_PENDING
        )
        self.message_user(request, f"{count} loan(s) marked as awaiting deposit.")
    mark_deposit_pending.short_description = "Mark selected as awaiting deposit"
