# OTT Referral System - Complete Setup Guide

## 🎯 System Overview

This is a production-ready referral and admin panel system for a Telegram-based OTT subscription business.

### Business Logic
- **Product**: Combo OTT Plan
- **Selling Price**: ₹135
- **Making Cost**: ₹42
- **Profit**: ₹93
- **Level 1 Commission**: 30% of profit = ₹28
- **Level 2 Commission**: 10% of profit = ₹9
- **Commission Hold Period**: 24 hours
- **Minimum Withdrawal**: ₹500

### Tech Stack
- **Backend**: Python FastAPI
- **Database**: PostgreSQL
- **Frontend**: React + Tailwind CSS
- **ORM**: SQLAlchemy
- **Authentication**: JWT

---

## 📦 Installation

### Prerequisites
- Python 3.9+
- PostgreSQL 13+
- Node.js 16+
- npm or yarn

### 1. Database Setup

```bash
# Create PostgreSQL database
createdb ottsonly_referral

# Run schema
psql -d ottsonly_referral -f referral_system/database/schema.sql
```

### 2. Backend Setup

```bash
cd referral_system/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run migrations (if using Alembic)
alembic upgrade head

# Start backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: http://localhost:8000

API Documentation: http://localhost:8000/docs

### 3. Frontend Setup

```bash
cd referral_system/frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at: http://localhost:3000

---

## 🔐 Initial Admin Setup

### Create Super Admin

Default credentials (change these immediately):
- **Telegram ID**: Set in `.env` as `SUPER_ADMIN_TELEGRAM_ID`
- **Password**: Set in `.env` as `SUPER_ADMIN_PASSWORD`

First login will auto-create the super admin account.

---

## 🚀 API Endpoints

### Authentication
- `POST /admin/auth/login` - Admin login

### Dashboard
- `GET /admin/dashboard/stats` - Dashboard statistics
- `GET /admin/dashboard/users` - User list with filters
- `GET /admin/dashboard/orders` - Order list
- `GET /admin/dashboard/referrers` - Referrer performance
- `GET /admin/dashboard/payment-monitoring` - Payment stats
- `GET /admin/dashboard/kpi` - KPI metrics

### Users
- `POST /users/create` - Create new user
- `GET /users/{telegram_id}` - Get user details
- `GET /users/{telegram_id}/referral-stats` - Referral stats
- `GET /users/{telegram_id}/referral-tree` - Referral tree

### Orders
- `POST /orders/create` - Create order
- `POST /orders/{order_id}/payment-success` - Mark payment successful
- `GET /orders/{order_id}` - Get order details

### Wallet
- `GET /wallet/{user_id}` - Get wallet balance
- `GET /wallet/{user_id}/transactions` - Transaction history

### Withdrawals
- `POST /withdrawals/create` - Create withdrawal request
- `GET /withdrawals/admin/all` - Get all withdrawals (admin)
- `POST /withdrawals/{id}/approve` - Approve withdrawal
- `POST /withdrawals/{id}/reject` - Reject withdrawal
- `POST /withdrawals/{id}/paid` - Mark as paid

### Fraud Detection
- `GET /fraud/flags` - Get all fraud flags
- `POST /fraud/flags/create` - Create manual flag
- `POST /fraud/user/{user_id}/block` - Block user
- `POST /fraud/user/{user_id}/run-checks` - Run fraud checks

### Settings
- `GET /settings/all` - Get all settings
- `PUT /settings/{key}` - Update setting

---

## 🔄 Integration with Telegram Bot

### User Registration

When a user starts the bot with `/start ref_XXXXX`:

```python
import requests

# Create user in referral system
response = requests.post('http://localhost:8000/users/create', json={
    'telegram_id': user.id,
    'username': user.username,
    'first_name': user.first_name,
    'last_name': user.last_name,
    'referred_by_code': referral_code,  # Extract from /start command
    'device_id': device_id,  # Optional
    'ip_address': ip_address  # Optional
})

user_data = response.json()
referral_code = user_data['referral_code']
```

### Payment Processing

When payment is successful:

```python
# Create order
order_response = requests.post('http://localhost:8000/orders/create', json={
    'user_id': user_id,
    'payment_method': 'upi',
    'upi_id': upi_id,
    'transaction_id': transaction_id
})

order = order_response.json()

# Mark payment successful
success_response = requests.post(
    f"http://localhost:8000/orders/{order['order_id']}/payment-success",
    json={'transaction_id': transaction_id}
)
```

---

## ⚙️ Background Jobs

The system automatically runs scheduled jobs:

### Commission Processing
- **Frequency**: Every 1 hour
- **Purpose**: Convert pending commissions to withdrawable after 24 hours
- **Job**: `process_pending_commissions_job()`

---

## 🛡️ Security Features

1. **JWT Authentication** - Secure admin access
2. **Role-Based Access Control** - Admin/Super Admin roles
3. **SQL Injection Prevention** - SQLAlchemy ORM
4. **Input Validation** - Pydantic schemas
5. **Audit Logging** - All admin actions logged
6. **CORS Protection** - Configured for frontend domain

---

## 🔍 Fraud Detection

Automatic detection for:
1. **Duplicate UPI** - Same UPI used by multiple users
2. **Duplicate Device** - Same device for multiple accounts
3. **Duplicate IP** - Same IP for multiple accounts
4. **Low Conversion** - High referrals but low conversions
5. **Rapid Signups** - Too many referrals in short time

---

## 📊 Admin Panel Features

### 1. Dashboard
- Real-time statistics
- Today's performance
- Overall metrics
- KPI indicators
- Payment monitoring

### 2. User Management
- View all users
- Filter by type, status
- Search functionality
- Mark suspicious users

### 3. Order Management
- View all orders
- Filter by status
- Payment tracking
- Commission status

### 4. Referrer Tracking
- Performance metrics
- Conversion rates
- Commission earned
- Referral tree

### 5. Withdrawal Management
- Pending requests
- Approve/Reject
- Mark as paid
- Transaction history

### 6. Fraud Detection
- View all flags
- Resolve flags
- Block/Unblock users
- Manual flag creation

### 7. System Settings
- Adjust commission rates
- Change prices
- Enable/disable features
- Minimum withdrawal amount

---

## 🗃️ Database Tables

1. **users** - All users (customers, referrers, admins)
2. **referrals** - Referral clicks and conversions
3. **orders** - Purchase orders
4. **wallets** - User wallet balances
5. **wallet_transactions** - All wallet transactions
6. **withdrawals** - Withdrawal requests
7. **fraud_flags** - Suspicious activity flags
8. **admin_logs** - Audit trail
9. **system_settings** - Configuration
10. **referral_stats** - Cached referral metrics

---

## 🚀 Production Deployment

### Using Docker (Recommended)

```bash
# Build and run
docker-compose up -d
```

### Manual Deployment

1. **Backend**:
```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

2. **Frontend**:
```bash
npm run build
# Serve build folder with nginx or similar
```

3. **Database**:
- Use managed PostgreSQL (AWS RDS, DigitalOcean, etc.)
- Enable backups
- Set up replication

4. **Background Jobs**:
- Run as systemd service or supervisor
- Monitor with cron or similar

---

## 📈 Monitoring

### Logs
- Backend logs: Check uvicorn/gunicorn logs
- Database logs: PostgreSQL logs
- Admin actions: Check `admin_logs` table

### Metrics to Monitor
- New users per day
- Conversion rate
- Revenue and profit
- Pending commissions
- Withdrawal processing time
- API response times

---

## 🔧 Troubleshooting

### Commission Not Processing
```bash
# Manually trigger commission processing
python -c "from app.services import PaymentService; from app.database import SessionLocal; db = SessionLocal(); PaymentService.process_pending_commissions(db)"
```

### Reset Admin Password
Update directly in database or use:
```python
from app.auth import get_password_hash
# Update user password in database
```

---

## 📞 Support

For issues or questions:
1. Check API documentation: http://localhost:8000/docs
2. Review logs for errors
3. Check database constraints
4. Verify environment variables

---

## ⚡ Quick Start Commands

```bash
# Backend
cd referral_system/backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload

# Frontend (new terminal)
cd referral_system/frontend
npm install
npm run dev

# Database
psql -d ottsonly_referral -f referral_system/database/schema.sql
```

---

## 📝 License

Proprietary - All rights reserved

---

**Built for production, secured, and ready to scale! 🚀**
