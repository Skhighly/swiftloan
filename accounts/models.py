from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    # Onboarding steps
    STEP_REGISTERED = 'registered'
    STEP_PROFILE = 'profile'
    STEP_ID_UPLOAD = 'id_upload'
    STEP_VERIFICATION = 'verification'
    STEP_JOB_INFO = 'job_info'
    STEP_COMPLETE = 'complete'

    ONBOARDING_STEPS = [
        (STEP_REGISTERED, 'Registered'),
        (STEP_PROFILE, 'Profile Submitted'),
        (STEP_ID_UPLOAD, 'ID Uploaded'),
        (STEP_VERIFICATION, 'Verification'),
        (STEP_JOB_INFO, 'Job Info Submitted'),
        (STEP_COMPLETE, 'Onboarding Complete'),
    ]

    onboarding_step = models.CharField(
        max_length=20, choices=ONBOARDING_STEPS, default=STEP_REGISTERED
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()

    def __str__(self):
        return self.email

    def get_onboarding_url(self):
        from django.urls import reverse
        step_urls = {
            self.STEP_REGISTERED: reverse('accounts:profile_setup'),
            self.STEP_PROFILE: reverse('accounts:id_upload'),
            self.STEP_ID_UPLOAD: reverse('accounts:verification'),
            self.STEP_VERIFICATION: reverse('accounts:job_info'),
            self.STEP_JOB_INFO: reverse('loans:apply'),
            self.STEP_COMPLETE: reverse('loans:dashboard'),
        }
        return step_urls.get(self.onboarding_step, reverse('loans:dashboard'))


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    id_front = models.ImageField(upload_to='id_documents/front/', blank=True, null=True)
    id_back = models.ImageField(upload_to='id_documents/back/', blank=True, null=True)
    mpesa_number = models.CharField(max_length=15, blank=True)
    kra_pin = models.CharField(max_length=20, blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    employer_name = models.CharField(max_length=200, blank=True)
    monthly_income = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile - {self.user.email}"
