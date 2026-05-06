from celery import shared_task
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


def _do_approve(loan):
    """
    Core approval logic shared by the Celery task and the view-level fallback.
    Approves the loan and creates the notification.
    """
    from notifications.models import Notification

    loan.status = loan.STATUS_APPROVED
    loan.approved_at = timezone.now()
    loan.save(update_fields=['status', 'approved_at'])

    Notification.objects.create(
        user=loan.user,
        title="🎉 Loan Approved!",
        message=(
            f"Congratulations! Your loan application of KES {loan.requested_amount:,} "
            f"has been approved. Please pay the refundable deposit of "
            f"KES {loan.deposit_amount:,.0f} to unlock your funds."
        ),
        notification_type=Notification.TYPE_APPROVAL,
        loan=loan,
    )
    logger.info("Loan #%s auto-approved.", loan.pk)


@shared_task(bind=True, max_retries=3)
def auto_approve_loan(self, loan_id):
    """
    Celery task: approves the loan after AUTO_APPROVAL_MINUTES.
    Scheduled via apply_async(countdown=...) in loans/views.py.

    Works when Redis is running and a celery worker is started.
    Falls back gracefully via check_and_approve_pending() if worker is absent.
    """
    from .models import LoanApplication
    try:
        loan = LoanApplication.objects.get(pk=loan_id)
        if loan.status == LoanApplication.STATUS_UNDER_REVIEW:
            _do_approve(loan)
    except LoanApplication.DoesNotExist:
        logger.warning("auto_approve_loan: Loan #%s not found.", loan_id)
    except Exception as exc:
        logger.exception("auto_approve_loan: error for loan #%s", loan_id)
        raise self.retry(exc=exc, countdown=30)


def check_and_approve_pending(loan):
    """
    View-level fallback — called on every detail/dashboard/history page load.

    If the loan has been under review longer than AUTO_APPROVAL_MINUTES and the
    Celery task never fired (no Redis / no worker running), approve it now.
    This makes auto-approval work with zero infrastructure in local development.

    Returns True if approval was triggered, False otherwise.
    """
    from django.conf import settings

    if loan.status != loan.STATUS_UNDER_REVIEW:
        return False

    minutes = getattr(settings, 'AUTO_APPROVAL_MINUTES', 5)
    elapsed = timezone.now() - loan.submitted_at

    if elapsed.total_seconds() >= minutes * 60:
        _do_approve(loan)
        loan.refresh_from_db()
        return True

    return False
