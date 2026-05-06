from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import User, UserProfile


class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter password'})
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm password'})
    )

    class Meta:
        model = User
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'Enter your email'})
        }

    def clean_password2(self):
        p1 = self.cleaned_data.get('password1')
        p2 = self.cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match.")
        return p2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'placeholder': 'Enter your email', 'autofocus': True})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password'})
    )


class ProfileSetupForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['full_name', 'phone_number']
        widgets = {
            'full_name': forms.TextInput(attrs={'placeholder': 'Your full legal name'}),
            'phone_number': forms.TextInput(attrs={'placeholder': '07XXXXXXXX'}),
        }


class IDUploadForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['id_front', 'id_back']

    def clean_id_front(self):
        img = self.cleaned_data.get('id_front')
        if img and img.size > 5 * 1024 * 1024:
            raise forms.ValidationError("Image must be under 5MB.")
        return img

    def clean_id_back(self):
        img = self.cleaned_data.get('id_back')
        if img and img.size > 5 * 1024 * 1024:
            raise forms.ValidationError("Image must be under 5MB.")
        return img


class VerificationForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['mpesa_number', 'kra_pin']
        widgets = {
            'mpesa_number': forms.TextInput(attrs={'placeholder': '2547XXXXXXXX'}),
            'kra_pin': forms.TextInput(attrs={'placeholder': 'A00XXXXXXXXX'}),
        }

    def clean_mpesa_number(self):
        num = self.cleaned_data.get('mpesa_number', '')
        num = num.strip()
        if not (num.startswith('2547') or num.startswith('07') or num.startswith('+2547')):
            raise forms.ValidationError("Enter a valid Safaricom M-Pesa number.")
        return num

    def clean_kra_pin(self):
        pin = self.cleaned_data.get('kra_pin', '').strip().upper()
        if len(pin) < 10:
            raise forms.ValidationError("Enter a valid KRA PIN (minimum 10 characters).")
        return pin


class JobInfoForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['job_title', 'employer_name', 'monthly_income']
        widgets = {
            'job_title': forms.TextInput(attrs={'placeholder': 'e.g. Software Engineer'}),
            'employer_name': forms.TextInput(attrs={'placeholder': 'Company / Organization name'}),
            'monthly_income': forms.NumberInput(attrs={'placeholder': 'Monthly gross income (KES)'}),
        }
