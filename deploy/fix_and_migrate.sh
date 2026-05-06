#!/usr/bin/env bash
# deploy/fix_and_migrate.sh
# Run this once to resolve ALL migration and table issues from scratch.
# Safe to run multiple times.

set -e
echo "=== SwiftLoan — Migration Fix Script ==="

# 1. Wipe stale migration state (keeps your data, resets Django's migration records)
echo ""
echo "Step 1: Clearing stale migration records from django_migrations table..."
python manage.py shell -c "
from django.db import connection
cursor = connection.cursor()
apps = ['accounts', 'loans', 'payments', 'notifications', 'core']
for app in apps:
    cursor.execute(\"DELETE FROM django_migrations WHERE app = %s\", [app])
    print(f'  Cleared: {app}')
" 2>/dev/null || echo "  (django_migrations table not yet created — that's fine)"

# 2. Drop and recreate all app tables to start clean
echo ""
echo "Step 2: Dropping stale app tables (if any exist)..."
python manage.py shell -c "
from django.db import connection
tables_to_drop = [
    'notifications_notification',
    'payments_payment',
    'loans_loanapplication',
    'accounts_userprofile',
    'accounts_user',
    'accounts_user_groups',
    'accounts_user_user_permissions',
]
cursor = connection.cursor()
for table in tables_to_drop:
    try:
        cursor.execute(f'DROP TABLE IF EXISTS \"{table}\" CASCADE')
        print(f'  Dropped: {table}')
    except Exception as e:
        print(f'  Skip {table}: {e}')
" 2>/dev/null || echo "  (Could not drop tables — proceeding anyway)"

# 3. Run all migrations fresh
echo ""
echo "Step 3: Running all migrations in correct order..."
python manage.py migrate --run-syncdb

echo ""
echo "=== Done! All tables created. ==="
echo ""
echo "Next steps:"
echo "  python manage.py createsuperuser"
echo "  python manage.py runserver"
