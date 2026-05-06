from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, LoginForm, ProfileSetupForm, IDUploadForm, VerificationForm, JobInfoForm
from .models import User, UserProfile


def register_view(request):
    if request.user.is_authenticated:
        return redirect('loans:dashboard')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.get_or_create(user=user)
            login(request, user)
            messages.success(request, "Account created! Let's set up your profile.")
            return redirect('accounts:profile_setup')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect(request.user.get_onboarding_url())
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.full_name or user.email}!")
            return redirect(user.get_onboarding_url())
        else:
            messages.error(request, "Invalid email or password.")
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('core:home')


@login_required
def profile_setup_view(request):
    if request.method == 'POST':
        form = ProfileSetupForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            request.user.onboarding_step = User.STEP_PROFILE
            request.user.save()
            messages.success(request, "Profile saved! Now upload your ID.")
            return redirect('accounts:id_upload')
    else:
        form = ProfileSetupForm(instance=request.user)
    return render(request, 'accounts/profile_setup.html', {'form': form, 'step': 1})


@login_required
def id_upload_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = IDUploadForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            request.user.onboarding_step = User.STEP_ID_UPLOAD
            request.user.save()
            messages.success(request, "ID uploaded! Now verify your M-Pesa and KRA PIN.")
            return redirect('accounts:verification')
    else:
        form = IDUploadForm(instance=profile)
    return render(request, 'accounts/id_upload.html', {'form': form, 'step': 2})


@login_required
def verification_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = VerificationForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            request.user.onboarding_step = User.STEP_VERIFICATION
            request.user.save()
            messages.success(request, "Verification info saved! Almost there.")
            return redirect('accounts:job_info')
    else:
        form = VerificationForm(instance=profile)
    return render(request, 'accounts/verification.html', {'form': form, 'step': 3})


@login_required
def job_info_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = JobInfoForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            request.user.onboarding_step = User.STEP_JOB_INFO
            request.user.save()
            messages.success(request, "All info received! You can now apply for a loan.")
            return redirect('loans:apply')
    else:
        form = JobInfoForm(instance=profile)
    return render(request, 'accounts/job_info.html', {'form': form, 'step': 4})
