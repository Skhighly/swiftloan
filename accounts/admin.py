from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ('mpesa_number', 'kra_pin', 'job_title', 'employer_name', 'monthly_income',
              'id_front', 'id_back', 'is_verified')


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = [UserProfileInline]
    list_display = ('email', 'full_name', 'phone_number', 'onboarding_step', 'is_active', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'onboarding_step')
    search_fields = ('email', 'full_name', 'phone_number')
    ordering = ('-date_joined',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('full_name', 'phone_number')}),
        ('Onboarding', {'fields': ('onboarding_step',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'mpesa_number', 'kra_pin', 'job_title', 'is_verified')
    list_filter = ('is_verified',)
    search_fields = ('user__email', 'mpesa_number', 'kra_pin')
    actions = ['mark_verified']

    def mark_verified(self, request, queryset):
        queryset.update(is_verified=True)
        self.message_user(request, f"{queryset.count()} profile(s) marked as verified.")
    mark_verified.short_description = "Mark selected profiles as verified"
