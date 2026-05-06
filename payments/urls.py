from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('deposit/<int:loan_pk>/', views.deposit_view, name='deposit'),
    path('awaiting/<int:payment_pk>/', views.awaiting_view, name='awaiting'),
    path('simulate-confirm/<int:payment_pk>/', views.simulate_confirm_view, name='simulate_confirm'),
    path('callback/', views.mpesa_callback_view, name='mpesa_callback'),
    path('status/<int:payment_pk>/', views.payment_status_api, name='payment_status'),
]
