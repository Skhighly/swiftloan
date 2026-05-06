from django import forms
from .models import LoanApplication
from django.conf import settings


class LoanApplicationForm(forms.ModelForm):
    LOAN_AMOUNTS = [(a, f"KES {a:,}") for a in getattr(settings, 'LOAN_AMOUNTS', [3000, 5000, 10000, 20000])]

    requested_amount = forms.ChoiceField(
        choices=LOAN_AMOUNTS,
        widget=forms.RadioSelect(attrs={'class': 'loan-amount-radio'}),
        label="Select Loan Amount"
    )
    reason = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 4,
            'placeholder': 'Briefly describe why you need this loan...'
        }),
        label="Reason for Application"
    )

    class Meta:
        model = LoanApplication
        fields = ['requested_amount', 'reason']

    def clean_requested_amount(self):
        amount = int(self.cleaned_data['requested_amount'])
        allowed = getattr(settings, 'LOAN_AMOUNTS', [3000, 5000, 10000, 20000])
        if amount not in allowed:
            raise forms.ValidationError("Please select a valid loan amount.")
        return amount


class RepaymentForm(forms.ModelForm):
    class Meta:
        model = LoanApplication
        fields = ['repayment_amount', 'repayment_reference']
        widgets = {
            'repayment_amount': forms.NumberInput(attrs={'placeholder': 'Amount paid (KES)'}),
            'repayment_reference': forms.TextInput(attrs={'placeholder': 'M-Pesa transaction code e.g. QHX1234ABC'}),
        }
        labels = {
            'repayment_amount': 'Amount Paid (KES)',
            'repayment_reference': 'M-Pesa Transaction Reference',
        }
