from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('setup/profile/', views.profile_setup_view, name='profile_setup'),
    path('setup/id-upload/', views.id_upload_view, name='id_upload'),
    path('setup/verification/', views.verification_view, name='verification'),
    path('setup/job-info/', views.job_info_view, name='job_info'),
]
