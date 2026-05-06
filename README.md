# ⚡ SwiftLoan — Django Loan Management System

Fast, transparent, and M-Pesa integrated loan application platform built for Kenya.

---

## 🗂 Project Structure

```
swiftloan/
├── accounts/          # Custom user model, onboarding (4 steps)
├── loans/             # Loan application, dashboard, history, repayment
├── payments/          # M-Pesa STK Push, deposit handling, callbacks
├── notifications/     # In-app notifications with unread badge
├── core/              # Public landing page, requirements, about
├── swiftloan/         # Django settings, URLs, Celery config
├── templates/         # All HTML templates
├── static/            # CSS, JS, images
├── media/             # User-uploaded ID documents
├── requirements.txt
├── Procfile
└── .env.example
```

---

## ⚙️ Setup Instructions

### 1. Clone & Create Virtual Environment
```bash
git clone <your-repo>
cd swiftloan
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
cp .env.example .env
# Edit .env with your actual values
```

### 4. Setup PostgreSQL
```sql
CREATE DATABASE swiftloan_db;
CREATE USER swiftloan_user WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE swiftloan_db TO swiftloan_user;
```

Update `DATABASE_URL` in `.env`:
```
DATABASE_URL=postgres://swiftloan_user:yourpassword@localhost:5432/swiftloan_db
```

### 5. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser (Admin)
```bash
python manage.py createsuperuser
```

### 7. Collect Static Files
```bash
python manage.py collectstatic
```

### 8. Start Redis (for Celery)
```bash
# macOS
brew services start redis

# Ubuntu/Debian
sudo service redis-server start

# Docker
docker run -d -p 6379:6379 redis
```

### 9. Start All Services
```bash
# Terminal 1 — Django dev server
python manage.py runserver

# Terminal 2 — Celery worker (auto-approval task)
celery -A swiftloan worker --loglevel=info

# Terminal 3 — Celery beat (scheduler, optional)
celery -A swiftloan beat --loglevel=info
```

---

## 🌐 URLs

| URL | Description |
|-----|-------------|
| `/` | Public landing page |
| `/requirements/` | Loan requirements |
| `/accounts/register/` | User registration |
| `/accounts/login/` | Login |
| `/accounts/setup/profile/` | Onboarding step 1 |
| `/accounts/setup/id-upload/` | Onboarding step 2 |
| `/accounts/setup/verification/` | Onboarding step 3 |
| `/accounts/setup/job-info/` | Onboarding step 4 |
| `/loans/dashboard/` | User dashboard |
| `/loans/apply/` | Loan application |
| `/loans/<id>/` | Loan detail |
| `/loans/history/` | Loan history |
| `/loans/<id>/repay/` | Repayment form |
| `/payments/deposit/<loan_id>/` | Deposit payment |
| `/payments/callback/` | M-Pesa Daraja callback |
| `/notifications/` | Notifications list |
| `/admin/` | Django admin (Jazzmin) |

---

## 💳 M-Pesa Integration

Get your Daraja API credentials from [developer.safaricom.co.ke](https://developer.safaricom.co.ke):

```env
MPESA_CONSUMER_KEY=your_consumer_key
MPESA_CONSUMER_SECRET=your_consumer_secret
MPESA_SHORTCODE=174379
MPESA_PASSKEY=your_passkey
MPESA_CALLBACK_URL=https://yourdomain.com/payments/callback/
MPESA_ENVIRONMENT=sandbox   # or 'production'
```

> **During development**, if credentials are not set, the "Simulate Payment" button appears on the awaiting screen so you can test the full flow without real M-Pesa credentials.

---

## 🏦 Loan Qualification Tiers

| Monthly Income | Max Loan | 10% Deposit |
|---------------|----------|------------|
| Below KES 10,000 | KES 3,000 | KES 300 |
| KES 10,000 – 24,999 | KES 5,000 | KES 500 |
| KES 25,000 – 49,999 | KES 10,000 | KES 1,000 |
| KES 50,000+ | KES 20,000 | KES 2,000 |

---

## 🔄 Loan Lifecycle

```
Submitted → Under Review → [Auto-approved in 5 min] → Approved
→ Deposit Pending → Deposit Paid → [Admin disburses] → Disbursed
→ [User repays manually] → Repaid ✓
```

---

## 🛡 Admin Panel (Jazzmin)

Visit `/admin/` — features:
- **Approve / Reject** loans in bulk
- **Mark Disbursed** after sending via M-Pesa
- View all payments and M-Pesa receipts
- Manage notifications
- Verify user profiles

---

## 🚀 Production Deployment

```bash
# .env
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
SECRET_KEY=your-very-secret-key

# Collect statics
python manage.py collectstatic --no-input

# Run with Gunicorn
gunicorn swiftloan.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

---

## 📦 Tech Stack

| Package | Purpose |
|---------|---------|
| Django 4.2 | Web framework |
| PostgreSQL | Database |
| Celery + Redis | Auto-approval async task |
| django-jazzmin | Beautiful admin UI |
| django-widget-tweaks | Form rendering |
| whitenoise | Static file serving |
| dj-database-url | DB config from URL |
| psycopg2 | PostgreSQL adapter |
| python-decouple | Environment variables |
| Pillow | Image handling (ID uploads) |
| Bootstrap 5.3 | Frontend CSS framework |
| Font Awesome 6 | Icons |

---

## 📝 License

MIT License — Free to use and modify.
