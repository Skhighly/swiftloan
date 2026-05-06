from pathlib import Path
from decouple import config
import dj_database_url
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='django-insecure-swiftloan-dev-key-change-in-production')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='*').split(',')

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'widget_tweaks',
    'accounts',
    'loans',
    'payments',
    'notifications',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'swiftloan.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.media',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'notifications.context_processors.notifications_processor',
            ],
        },
    },
]

WSGI_APPLICATION = 'swiftloan.wsgi.application'

DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL', default='sqlite:///db.sqlite3')
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_TZ = True

# ── Static Files ──────────────────────────────────────────────────────────────
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Dev: plain storage — no manifest hashing, no chasing .map files from jazzmin vendor CSS
# Prod: CompressedStaticFilesStorage compresses but does NOT do manifest hashing,
#       so it never errors on missing .map source map files from jazzmin/bootstrap
if DEBUG:
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
else:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# Tell whitenoise never to compress or fingerprint these extensions
WHITENOISE_SKIP_COMPRESS_EXTENSIONS = [
    'map', 'gz', 'br', 'png', 'jpg', 'jpeg', 'gif', 'webp', 'ico', 'woff', 'woff2',
]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'accounts.User'
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/loans/dashboard/'
LOGOUT_REDIRECT_URL = '/'

# ── Celery + Redis ────────────────────────────────────────────────────────────
# Redis is an OS-level service (brew install redis / apt install redis-server).
# django-redis is the Python client that connects to it.
# If REDIS_URL is not set, tasks run inline with no worker needed — good for local dev.
_REDIS_URL = config('REDIS_URL', default='')

if _REDIS_URL:
    # Full async mode — requires redis-server running + celery worker process
    CELERY_BROKER_URL     = _REDIS_URL
    CELERY_RESULT_BACKEND = _REDIS_URL
    CELERY_TASK_ALWAYS_EAGER = False
else:
    # No Redis — tasks execute immediately inline in the same process.
    # Auto-approval fires right away. No worker or Redis needed for dev.
    CELERY_BROKER_URL            = 'memory://'
    CELERY_RESULT_BACKEND        = 'cache+memory://'
    CELERY_TASK_ALWAYS_EAGER     = True
    CELERY_TASK_EAGER_PROPAGATES = True

CELERY_TIMEZONE        = 'Africa/Nairobi'
CELERY_ACCEPT_CONTENT  = ['json']
CELERY_TASK_SERIALIZER = 'json'

# ── M-Pesa (Daraja API) ───────────────────────────────────────────────────────
# Switch sandbox <-> live with one line: MPESA_ENVIRONMENT=sandbox|production
MPESA_CONSUMER_KEY    = config('MPESA_CONSUMER_KEY', default='')
MPESA_CONSUMER_SECRET = config('MPESA_CONSUMER_SECRET', default='')
MPESA_SHORTCODE       = config('MPESA_SHORTCODE', default='174379')
MPESA_PASSKEY         = config('MPESA_PASSKEY', default='')
MPESA_CALLBACK_URL    = config('MPESA_CALLBACK_URL', default='https://yourdomain.com/payments/callback/')
MPESA_ENVIRONMENT     = config('MPESA_ENVIRONMENT', default='sandbox')

# ── Loan Settings ─────────────────────────────────────────────────────────────
LOAN_AMOUNTS          = [3000, 5000, 10000, 20000]
DEPOSIT_PERCENTAGE    = 10
AUTO_APPROVAL_MINUTES = 5

# ── Jazzmin Admin ─────────────────────────────────────────────────────────────
JAZZMIN_SETTINGS = {
    "site_title": "SwiftLoan Admin",
    "site_header": "SwiftLoan",
    "site_brand": "SwiftLoan",
    "welcome_sign": "Welcome to SwiftLoan Admin Panel",
    "copyright": "SwiftLoan Ltd",
    "search_model": ["accounts.User", "loans.LoanApplication"],
    "topmenu_links": [
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Site", "url": "/", "new_window": True},
    ],
    "show_sidebar": True,
    "navigation_expanded": True,
    "order_with_respect_to": ["accounts", "loans", "payments", "notifications"],
    "icons": {
        "auth": "fas fa-users-cog",
        "accounts.user": "fas fa-user",
        "loans.loanapplication": "fas fa-file-invoice-dollar",
        "payments.payment": "fas fa-credit-card",
        "notifications.notification": "fas fa-bell",
    },
    "default_icon_parents":  "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    "related_modal_active": False,
    "show_ui_builder": False,
    "changeform_format": "horizontal_tabs",
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "body_small_text": False,
    "brand_colour": "navbar-success",
    "accent": "accent-teal",
    "navbar": "navbar-dark",
    "navbar_fixed": True,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-success",
    "sidebar_nav_child_indent": True,
}
