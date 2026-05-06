import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils import timezone
from loans.models import LoanApplication
from notifications.models import Notification
from .models import Payment
from .mpesa import initiate_stk_push


@login_required
def deposit_view(request, loan_pk):
    loan = get_object_or_404(LoanApplication, pk=loan_pk, user=request.user)

    if loan.status not in [LoanApplication.STATUS_APPROVED, LoanApplication.STATUS_DEPOSIT_PENDING]:
        messages.error(request, "This loan is not eligible for a deposit payment.")
        return redirect('loans:detail', pk=loan_pk)

    # Ensure loan is in deposit_pending
    if loan.status == LoanApplication.STATUS_APPROVED:
        loan.status = LoanApplication.STATUS_DEPOSIT_PENDING
        loan.save()

    # Check if deposit already made
    existing = Payment.objects.filter(
        loan=loan,
        payment_type=Payment.TYPE_DEPOSIT,
        status=Payment.STATUS_COMPLETED
    ).first()
    if existing:
        messages.info(request, "Deposit already paid for this loan.")
        return redirect('loans:detail', pk=loan_pk)

    phone = ''
    try:
        phone = request.user.profile.mpesa_number or ''
    except Exception:
        pass

    if request.method == 'POST':
        phone_input = request.POST.get('phone_number', phone).strip()
        payment = Payment.objects.create(
            user=request.user,
            loan=loan,
            payment_type=Payment.TYPE_DEPOSIT,
            amount=loan.deposit_amount,
            phone_number=phone_input,
            status=Payment.STATUS_PENDING,
        )

        result = initiate_stk_push(
            phone_number=phone_input,
            amount=loan.deposit_amount,
            account_reference=f"SL-DEP-{loan.pk}",
            description=f"SwiftLoan deposit for loan #{loan.pk}",
        )

        if result.get('success'):
            payment.mpesa_checkout_request_id = result.get('checkout_request_id', '')
            payment.mpesa_merchant_request_id = result.get('merchant_request_id', '')
            payment.save()
            messages.success(
                request,
                "STK Push sent to your phone! Enter your M-Pesa PIN to complete the payment. "
                "Your loan status will update to Pending once confirmed."
            )
            return redirect('payments:awaiting', payment_pk=payment.pk)
        else:
            # If no credentials yet, allow mock confirm for dev
            if result.get('mock'):
                messages.warning(
                    request,
                    "M-Pesa credentials not configured. In production, STK Push will be sent. "
                    "For now, use the 'Simulate Payment' button below."
                )
                return redirect('payments:awaiting', payment_pk=payment.pk)
            else:
                payment.status = Payment.STATUS_FAILED
                payment.save()
                messages.error(request, f"Payment initiation failed: {result.get('error')}")

    context = {
        'loan': loan,
        'phone': phone,
    }
    return render(request, 'payments/deposit.html', context)


@login_required
def awaiting_view(request, payment_pk):
    payment = get_object_or_404(Payment, pk=payment_pk, user=request.user)
    from django.conf import settings
    return render(request, 'payments/awaiting.html', {
        'payment': payment,
        'debug': settings.DEBUG,
    })


@login_required
def simulate_confirm_view(request, payment_pk):
    """Dev-only: simulate a successful M-Pesa callback."""
    payment = get_object_or_404(Payment, pk=payment_pk, user=request.user)
    if payment.status == Payment.STATUS_PENDING:
        payment.status = Payment.STATUS_COMPLETED
        payment.mpesa_receipt_number = f"SIM{payment.pk}ABCDEF"
        payment.save()

        loan = payment.loan
        if payment.payment_type == Payment.TYPE_DEPOSIT:
            loan.status = LoanApplication.STATUS_DEPOSIT_PAID
            loan.save()
            Notification.objects.create(
                user=request.user,
                title="💳 Deposit Confirmed!",
                message=(
                    f"Your deposit of KES {payment.amount:,.0f} for loan #{loan.pk} has been confirmed. "
                    "Your loan is now pending disbursement by our team."
                ),
                notification_type=Notification.TYPE_PAYMENT,
                loan=loan,
            )
            messages.success(request, "Deposit confirmed! Your loan is now pending disbursement.")

    return redirect('loans:detail', pk=payment.loan.pk)


@csrf_exempt
def mpesa_callback_view(request):
    """M-Pesa Daraja callback endpoint."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            stk_callback = data.get('Body', {}).get('stkCallback', {})
            checkout_request_id = stk_callback.get('CheckoutRequestID', '')
            result_code = stk_callback.get('ResultCode')

            payment = Payment.objects.filter(
                mpesa_checkout_request_id=checkout_request_id
            ).first()

            if payment:
                if result_code == 0:
                    payment.status = Payment.STATUS_COMPLETED
                    items = stk_callback.get('CallbackMetadata', {}).get('Item', [])
                    for item in items:
                        if item['Name'] == 'MpesaReceiptNumber':
                            payment.mpesa_receipt_number = item.get('Value', '')
                        if item['Name'] == 'TransactionDate':
                            payment.mpesa_transaction_date = str(item.get('Value', ''))
                    payment.save()

                    loan = payment.loan
                    if payment.payment_type == Payment.TYPE_DEPOSIT:
                        loan.status = LoanApplication.STATUS_DEPOSIT_PAID
                        loan.save()
                        Notification.objects.create(
                            user=payment.user,
                            title="💳 Deposit Confirmed!",
                            message=(
                                f"Your deposit of KES {payment.amount:,.0f} for loan #{loan.pk} "
                                "has been received. Your loan is pending disbursement."
                            ),
                            notification_type=Notification.TYPE_PAYMENT,
                            loan=loan,
                        )
                else:
                    payment.status = Payment.STATUS_FAILED
                    payment.save()

        except Exception as e:
            print(f"Callback error: {e}")

    return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Accepted'})


@login_required
def payment_status_api(request, payment_pk):
    payment = get_object_or_404(Payment, pk=payment_pk, user=request.user)
    return JsonResponse({'status': payment.status})
