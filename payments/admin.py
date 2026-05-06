from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'loan', 'payment_type', 'amount', 'status',
                    'mpesa_receipt_number', 'created_at')
    list_filter = ('payment_type', 'status', 'created_at')
    search_fields = ('user__email', 'mpesa_receipt_number', 'mpesa_checkout_request_id', 'phone_number')
    readonly_fields = ('created_at', 'updated_at', 'mpesa_checkout_request_id',
                       'mpesa_merchant_request_id', 'mpesa_receipt_number', 'mpesa_transaction_date')
    ordering = ('-created_at',)
