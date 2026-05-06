# swiftloan/settings.py — updated bottom section
# Replace the bottom of your existing settings.py with this import:
#
#   from .settings_security import *
#
# Then add this to .env:
#   ENVIRONMENT=local   or   ENVIRONMENT=production

# ══════════════════════════════════════════════════════════════════
#  HOW LOCAL ↔ PRODUCTION SWITCHING WORKS
# ══════════════════════════════════════════════════════════════════
#
#  .env (local):
#    DEBUG=True
#    DATABASE_URL=postgres://localhost/swiftloan_db
#    REDIS_URL=redis://localhost:6379/0
#    MPESA_ENVIRONMENT=sandbox
#    ALLOWED_HOSTS=localhost,127.0.0.1
#
#  .env.production (on server):
#    DEBUG=False
#    DATABASE_URL=postgres://user:pass@db-host/swiftloan_db
#    REDIS_URL=redis://:password@redis-host:6379/0
#    MPESA_ENVIRONMENT=production
#    ALLOWED_HOSTS=yourdomain.com
#    SECRET_KEY=<long-random-key>
#    LOG_DIR=/var/log/swiftloan
#
#  To run production locally (testing prod config without deploying):
#    cp .env.production .env.prod.local
#    DEBUG=True  # keep this True on local even when testing prod config
#    python manage.py runserver --settings=swiftloan.settings
#
# ══════════════════════════════════════════════════════════════════
#  SWITCHING MPESA: SANDBOX ↔ LIVE
# ══════════════════════════════════════════════════════════════════
#
#  The mpesa.py utility already reads MPESA_ENVIRONMENT from .env:
#    sandbox → https://sandbox.safaricom.co.ke
#    production → https://api.safaricom.co.ke
#
#  Sandbox credentials (free from developer.safaricom.co.ke):
#    MPESA_CONSUMER_KEY=<sandbox key>
#    MPESA_CONSUMER_SECRET=<sandbox secret>
#    MPESA_SHORTCODE=174379       # Safaricom test shortcode
#    MPESA_PASSKEY=<sandbox passkey>
#    MPESA_CALLBACK_URL=https://<ngrok-tunnel>/payments/callback/
#
#  Live credentials:
#    MPESA_CONSUMER_KEY=<live key>
#    MPESA_CONSUMER_SECRET=<live secret>
#    MPESA_SHORTCODE=<your paybill>
#    MPESA_PASSKEY=<your live passkey>
#    MPESA_CALLBACK_URL=https://yourdomain.com/payments/callback/
#
#  One-line switch: change MPESA_ENVIRONMENT=sandbox → production
# ══════════════════════════════════════════════════════════════════
