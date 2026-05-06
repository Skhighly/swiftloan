# accounts/rate_limits.py
# Apply these decorators to sensitive views

from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator

# ── Option A: django-ratelimit (recommended, pip install django-ratelimit) ────
# Usage on a view function:
#
#   from ratelimit.decorators import ratelimit
#
#   @ratelimit(key='ip', rate='5/m', method='POST', block=True)
#   def login_view(request): ...
#
#   @ratelimit(key='user', rate='3/h', method='POST', block=True)
#   def apply_view(request): ...   # max 3 loan applications per hour per user
#
#   @ratelimit(key='ip', rate='10/m', method='POST', block=True)
#   def mpesa_callback_view(request): ...

# ── Option B: Nginx rate limiting (production, no Django dependency) ──────────
# In your nginx.conf:
#
#   http {
#       limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;
#       limit_req_zone $binary_remote_addr zone=api:10m rate=30r/m;
#
#       server {
#           location /accounts/login/ {
#               limit_req zone=login burst=3 nodelay;
#           }
#           location /payments/callback/ {
#               limit_req zone=api burst=10 nodelay;
#               allow <safaricom_ip_range>;
#               deny all;
#           }
#       }
#   }

# ── RECOMMENDED RATE LIMITS FOR SWIFTLOAN ────────────────────────────────────
RATE_LIMITS = {
    'login':           '5/m',    # 5 attempts per minute per IP
    'register':        '3/m',    # 3 registrations per minute per IP
    'loan_apply':      '3/h',    # 3 applications per hour per user
    'mpesa_stk_push':  '3/m',    # 3 STK pushes per minute per user
    'mpesa_callback':  '60/m',   # Safaricom callbacks are high-volume
}
