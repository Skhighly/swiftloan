# swiftloan/settings_security.py
# Import this at the bottom of settings.py:
#   from .settings_security import *  (or paste inline)

from decouple import config

# ── HTTPS / HSTS ─────────────────────────────────────────────────────────────
# Only activate these when DEBUG=False and you have a real TLS cert
if not config('DEBUG', default=True, cast=bool):
    SECURE_SSL_REDIRECT = True                  # redirect all HTTP → HTTPS
    SECURE_HSTS_SECONDS = 31536000              # 1 year HSTS header
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SESSION_COOKIE_SECURE = True                # cookie only over HTTPS
    CSRF_COOKIE_SECURE = True                   # CSRF token only over HTTPS
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')  # trust proxy
else:
    # Local dev — allow HTTP
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

# ── SECURE COOKIES ────────────────────────────────────────────────────────────
SESSION_COOKIE_HTTPONLY = True          # JS cannot read the session cookie
CSRF_COOKIE_HTTPONLY = False            # Django needs JS to read CSRF in AJAX
SESSION_COOKIE_SAMESITE = 'Lax'        # CSRF mitigation
CSRF_COOKIE_SAMESITE = 'Lax'
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_AGE = 60 * 60 * 24 * 7  # 7 days

# ── CLICKJACKING PROTECTION ───────────────────────────────────────────────────
X_FRAME_OPTIONS = 'DENY'

# ── CONTENT SECURITY POLICY ──────────────────────────────────────────────────
# Requires django-csp: pip install django-csp
# Add 'csp.middleware.CSPMiddleware' to MIDDLEWARE
CSP_DEFAULT_SRC = ("'self'",)
CSP_STYLE_SRC = ("'self'", "https://fonts.googleapis.com",
                 "https://cdnjs.cloudflare.com", "'unsafe-inline'")
CSP_FONT_SRC = ("'self'", "https://fonts.gstatic.com",
                "https://cdnjs.cloudflare.com")
CSP_SCRIPT_SRC = ("'self'", "https://cdnjs.cloudflare.com")
CSP_IMG_SRC = ("'self'", "data:")

# ── ACCOUNT LOCKOUT ───────────────────────────────────────────────────────────
# Requires django-axes: pip install django-axes
# Add 'axes' to INSTALLED_APPS and 'axes.backends.AxesStandaloneBackend'
# to AUTHENTICATION_BACKENDS
AXES_FAILURE_LIMIT = 5                  # lock after 5 failed attempts
AXES_COOLOFF_TIME = 1                   # hours to stay locked
AXES_LOCKOUT_TEMPLATE = 'accounts/locked.html'
AXES_RESET_ON_SUCCESS = True

# ── LOGGING ───────────────────────────────────────────────────────────────────
import os
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} {name} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '[{asctime}] {levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(config('LOG_DIR', default='/tmp'), 'swiftloan.log'),
            'maxBytes': 10 * 1024 * 1024,   # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'security_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(config('LOG_DIR', default='/tmp'), 'security.log'),
            'maxBytes': 5 * 1024 * 1024,
            'backupCount': 10,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': config('DJANGO_LOG_LEVEL', default='INFO'),
            'propagate': True,
        },
        'django.security': {
            'handlers': ['security_file', 'console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'loans': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'payments': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'axes': {
            'handlers': ['security_file'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

# ── CACHING ───────────────────────────────────────────────────────────────────
# Uses Redis (same broker as Celery) for fast session/view caching
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': config('REDIS_URL', default='redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'swiftloan',
        'TIMEOUT': 300,  # 5 minutes default
    }
}
# Store sessions in Redis cache (fast + auto-expire)
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
