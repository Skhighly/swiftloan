#!/usr/bin/env bash
# deploy/dev_start.sh — start all local SwiftLoan services

# ── Colors ────────────────────────────────────────────────────────────────────
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'

echo -e "${GREEN}⚡ SwiftLoan — Local Development Start${NC}"
echo "────────────────────────────────────────────"

# 1. Check Redis
if ! redis-cli ping > /dev/null 2>&1; then
    echo -e "${YELLOW}Starting Redis...${NC}"
    redis-server --daemonize yes
else
    echo "✓ Redis already running"
fi

# 2. Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "✓ Virtual environment activated"
fi

# 3. Apply any pending migrations
python manage.py migrate --run-syncdb 2>/dev/null
echo "✓ Migrations up to date"

# 4. Start Celery worker in background
pkill -f "celery -A swiftloan" 2>/dev/null
celery -A swiftloan worker --loglevel=warning --detach \
    --logfile=/tmp/swiftloan_celery.log \
    --pidfile=/tmp/swiftloan_celery.pid
echo "✓ Celery worker started (log: /tmp/swiftloan_celery.log)"

# 5. Start Django dev server
echo ""
echo -e "${GREEN}Starting Django on http://127.0.0.1:8000${NC}"
echo "Admin: http://127.0.0.1:8000/admin/"
echo ""
echo "── M-Pesa callback testing ──────────────────"
echo "To test real STK push locally, expose via ngrok:"
echo "  1. Install: npm install -g ngrok  OR  brew install ngrok"
echo "  2. Authenticate: ngrok config add-authtoken <your-token>"
echo "  3. Expose:  ngrok http 8000"
echo "  4. Copy the https URL, set in .env:"
echo "     MPESA_CALLBACK_URL=https://<ngrok-id>.ngrok.io/payments/callback/"
echo "  5. Restart Django server"
echo ""
echo "── Quick switch: sandbox → production ──────"
echo "  In .env, change:"
echo "    MPESA_ENVIRONMENT=sandbox  →  MPESA_ENVIRONMENT=production"
echo "    MPESA_CONSUMER_KEY=<live key>"
echo "    MPESA_CONSUMER_SECRET=<live secret>"
echo "    MPESA_SHORTCODE=<your paybill>"
echo "────────────────────────────────────────────"

python manage.py runserver
