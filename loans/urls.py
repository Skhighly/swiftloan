from django.urls import path
from . import views

app_name = 'loans'

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('apply/', views.apply_view, name='apply'),
    path('<int:pk>/', views.detail_view, name='detail'),
    path('history/', views.history_view, name='history'),
    path('<int:pk>/repay/', views.repay_view, name='repay'),
]
