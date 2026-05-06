#!/usr/bin/env bash
# deploy/deploy_production.sh
# Run this on your Ubuntu 22.04 VPS to deploy SwiftLoan
# Usage: sudo bash deploy_production.sh yourdomain.com

DOMAIN=${1:-yourdomain.com}
APP_DIR=/home/swiftloan/app
VENV_DIR=$APP_DIR/venv
USER=swiftloan

echo "═══════════════════════════════════════════"
echo "  SwiftLoan Production Deployment"
echo "  Domain: $DOMAIN"
echo "═══════════════════════════════════════════"

# ── System packages ───────────────────────────────────────────────────────────
apt-get update -qq
apt-get install -y python3.11 python3.11-venv python3-pip nginx \
    postgresql postgresql-contrib redis-server certbot python3-certbot-nginx \
    supervisor libpq-dev

# ── Create app user ───────────────────────────────────────────────────────────
id -u $USER &>/dev/null || useradd -m -s /bin/bash $USER

# ── Python environment ────────────────────────────────────────────────────────
mkdir -p $APP_DIR
python3.11 -m venv $VENV_DIR
$VENV_DIR/bin/pip install -q --upgrade pip
$VENV_DIR/bin/pip install -q -r $APP_DIR/requirements.txt

# Add security packages
$VENV_DIR/bin/pip install -q \
    django-axes \
    django-csp \
    django-ratelimit \
    django-redis \
    sentry-sdk

# ── PostgreSQL ────────────────────────────────────────────────────────────────
sudo -u postgres psql -c "CREATE USER swiftloan_user WITH PASSWORD 'CHANGEME_STRONG_PASSWORD';" 2>/dev/null || true
sudo -u postgres psql -c "CREATE DATABASE swiftloan_db OWNER swiftloan_user;" 2>/dev/null || true
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE swiftloan_db TO swiftloan_user;" 2>/dev/null || true

# ── Redis (bind to localhost only) ────────────────────────────────────────────
sed -i 's/bind 127.0.0.1 ::1/bind 127.0.0.1/' /etc/redis/redis.conf
sed -i 's/# requirepass .*/requirepass CHANGEME_REDIS_PASSWORD/' /etc/redis/redis.conf
systemctl restart redis-server

# ── Django setup ──────────────────────────────────────────────────────────────
cd $APP_DIR
$VENV_DIR/bin/python manage.py migrate --noinput
$VENV_DIR/bin/python manage.py collectstatic --noinput
mkdir -p /var/log/swiftloan
chown -R $USER:$USER /var/log/swiftloan $APP_DIR

# ── Supervisor config (manages gunicorn + celery) ─────────────────────────────
cat > /etc/supervisor/conf.d/swiftloan.conf << 'EOF'
[program:swiftloan_web]
command=/home/swiftloan/app/venv/bin/gunicorn swiftloan.wsgi:application
    --bind 127.0.0.1:8000
    --workers 3
    --worker-class sync
    --timeout 120
    --access-logfile /var/log/swiftloan/gunicorn_access.log
    --error-logfile /var/log/swiftloan/gunicorn_error.log
directory=/home/swiftloan/app
user=swiftloan
autostart=true
autorestart=true
redirect_stderr=true

[program:swiftloan_celery]
command=/home/swiftloan/app/venv/bin/celery -A swiftloan worker
    --loglevel=info
    --logfile=/var/log/swiftloan/celery.log
    --concurrency=2
directory=/home/swiftloan/app
user=swiftloan
autostart=true
autorestart=true
redirect_stderr=true
environment=DJANGO_SETTINGS_MODULE="swiftloan.settings"
EOF

supervisorctl reread
supervisorctl update
supervisorctl start swiftloan_web
supervisorctl start swiftloan_celery

# ── Nginx ─────────────────────────────────────────────────────────────────────
cp $APP_DIR/deploy/nginx.conf /etc/nginx/sites-available/swiftloan
sed -i "s/yourdomain.com/$DOMAIN/g" /etc/nginx/sites-available/swiftloan
ln -sf /etc/nginx/sites-available/swiftloan /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl restart nginx

# ── TLS Certificate (free via Let's Encrypt) ──────────────────────────────────
certbot --nginx -d $DOMAIN --non-interactive --agree-tos \
    --email admin@$DOMAIN --redirect

# ── Firewall ──────────────────────────────────────────────────────────────────
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

echo ""
echo "✓ SwiftLoan deployed at https://$DOMAIN"
echo "✓ Admin panel: https://$DOMAIN/admin/"
echo ""
echo "⚠  Remember to:"
echo "  1. Edit /home/swiftloan/app/.env with production values"
echo "  2. Change PostgreSQL password in /etc/supervisor/conf.d/swiftloan.conf"
echo "  3. Change Redis password in /etc/redis/redis.conf and .env"
echo "  4. Run: python manage.py createsuperuser"
