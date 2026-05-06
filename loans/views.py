from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
from .models import LoanApplication
from .forms import LoanApplicationForm, RepaymentForm
from .tasks import auto_approve_loan, check_and_approve_pending


def _compute_qualified_amount(user):
    """
    Income-based qualification tiers.
    Returns the maximum loan amount the user qualifies for.
    """
    try:
        income = user.profile.monthly_income or 0
        if income >= 50000:
            return 20000
        elif income >= 25000:
            return 10000
        elif income >= 10000:
            return 5000
        else:
            return 3000
    except Exception:
        return 3000


@login_required
def dashboard_view(request):
    loans = LoanApplication.objects.filter(user=request.user)
    active_loan = loans.exclude(
        status__in=[LoanApplication.STATUS_REJECTED, LoanApplication.STATUS_REPAID]
    ).first()

    # Fallback approval check — works even without Celery/Redis
    if active_loan:
        check_and_approve_pending(active_loan)
        active_loan.refresh_from_db()

    context = {
        'loans': loans,
        'active_loan': active_loan,
        'user': request.user,
    }
    return render(request, 'loans/dashboard.html', context)


@login_required
def apply_view(request):
    # Block if user already has an active application
    existing = LoanApplication.objects.filter(
        user=request.user
    ).exclude(
        status__in=[LoanApplication.STATUS_REJECTED, LoanApplication.STATUS_REPAID]
    ).first()

    if existing:
        messages.info(request, "You already have an active loan application.")
        return redirect('loans:detail', pk=existing.pk)

    qualified_amount = _compute_qualified_amount(request.user)
    minutes = getattr(settings, 'AUTO_APPROVAL_MINUTES', 5)

    if request.method == 'POST':
        form = LoanApplicationForm(request.POST)
        if form.is_valid():
            loan = form.save(commit=False)
            loan.user = request.user
            loan.qualified_amount = qualified_amount
            loan.status = LoanApplication.STATUS_UNDER_REVIEW
            loan.save()

            # Schedule Celery task (works when Redis is available + worker is running)
            # If Redis is not available, CELERY_TASK_ALWAYS_EAGER=True fires it immediately
            auto_approve_loan.apply_async((loan.pk,), countdown=minutes * 60)

            messages.success(
                request,
                f"Application submitted! Your loan will be auto-approved in {minutes} "
                f"minutes. Refresh this page or check your Notifications tab."
            )
            return redirect('loans:detail', pk=loan.pk)
    else:
        form = LoanApplicationForm()

    context = {
        'form': form,
        'qualified_amount': qualified_amount,
        'loan_amounts': getattr(settings, 'LOAN_AMOUNTS', [3000, 5000, 10000, 20000]),
        'deposit_pct': getattr(settings, 'DEPOSIT_PERCENTAGE', 10),
    }
    return render(request, 'loans/apply.html', context)


@login_required
def detail_view(request, pk):
    loan = get_object_or_404(LoanApplication, pk=pk, user=request.user)

    # Fallback approval check on every page load
    check_and_approve_pending(loan)
    loan.refresh_from_db()

    # Fetch payments safely — guards against payments table not yet migrated
    try:
        from payments.models import Payment
        loan_payments = list(Payment.objects.filter(loan=loan))
    except Exception:
        loan_payments = []

    return render(request, 'loans/detail.html', {
        'loan': loan,
        'loan_payments': loan_payments,
    })


@login_required
def history_view(request):
    loans = LoanApplication.objects.filter(user=request.user)

    # Run fallback approval check on all under-review loans
    for loan in loans.filter(status=LoanApplication.STATUS_UNDER_REVIEW):
        check_and_approve_pending(loan)

    # Re-fetch after any approvals fired
    loans = LoanApplication.objects.filter(user=request.user)
    return render(request, 'loans/history.html', {'loans': loans})


@login_required
def repay_view(request, pk):
    loan = get_object_or_404(LoanApplication, pk=pk, user=request.user)

    if loan.status != LoanApplication.STATUS_DISBURSED:
        messages.error(request, "This loan is not eligible for repayment at this time.")
        return redirect('loans:detail', pk=pk)

    if request.method == 'POST':
        form = RepaymentForm(request.POST, instance=loan)
        if form.is_valid():
            loan = form.save(commit=False)
            loan.status = LoanApplication.STATUS_REPAID
            loan.repaid_at = timezone.now()
            loan.save()

            from notifications.models import Notification
            Notification.objects.create(
                user=request.user,
                title="✅ Repayment Received",
                message=(
                    f"Your repayment of KES {loan.repayment_amount:,} for loan #{loan.pk} "
                    f"(Ref: {loan.repayment_reference}) has been recorded. Thank you!"
                ),
                notification_type=Notification.TYPE_REPAYMENT,
                loan=loan,
            )
            messages.success(request, "Repayment submitted! Your loan is now marked as repaid.")
            return redirect('loans:history')
    else:
        form = RepaymentForm(instance=loan)

    return render(request, 'loans/repay.html', {'loan': loan, 'form': form})
