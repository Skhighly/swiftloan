from django.shortcuts import render
from django.conf import settings


def home_view(request):
    loan_amounts = getattr(settings, 'LOAN_AMOUNTS', [3000, 5000, 10000, 20000])
    deposit_pct = getattr(settings, 'DEPOSIT_PERCENTAGE', 10)
    return render(request, 'core/home.html', {
        'loan_amounts': loan_amounts,
        'deposit_pct': deposit_pct,
    })


def requirements_view(request):
    loan_amounts = getattr(settings, 'LOAN_AMOUNTS', [3000, 5000, 10000, 20000])
    deposit_pct = getattr(settings, 'DEPOSIT_PERCENTAGE', 10)
    return render(request, 'core/requirements.html', {
        'loan_amounts': loan_amounts,
        'deposit_pct': deposit_pct,
    })


def about_view(request):
    return render(request, 'core/about.html')
