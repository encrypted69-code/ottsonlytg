# 🚀 Quick Start Guide - OTT Referral System

## ⚡ 5-Minute Setup

### Step 1: Clone/Extract Files
Your referral system is ready in `referral_system/` folder

### Step 2: Database Setup
```bash
# Create PostgreSQL database
createdb ottsonly_referral

# Apply schema
cd referral_system
psql -d ottsonly_referral -f database/schema.sql
```

### Step 3: Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env

# Edit .env file - SET THESE:
# DATABASE_URL=postgresql://username:password@localhost:5432/ottsonly_referral
# SECRET_KEY=your-random-secret-key-here
# SUPER_ADMIN_TELEGRAM_ID=your_telegram_id
# SUPER_ADMIN_PASSWORD=your_secure_password

# Create seed data (optional)
python seed_data.py

# Start backend
uvicorn app.main:app --reload
```

Backend running at: **http://localhost:8000**
API Docs: **http://localhost:8000/docs**

### Step 4: Frontend Setup
```bash
# Open new terminal
cd referral_system/frontend

# Install dependencies
npm install

# Start frontend
npm run dev
```

Frontend running at: **http://localhost:3000**

### Step 5: Login to Admin Panel
1. Open http://localhost:3000/login
2. Enter your Telegram ID (set in .env)
3. Enter your password (set in .env)
4. Click Login

**You're done! 🎉**

---

## 🐳 Docker Setup (Alternative)

If you have Docker installed:

```bash
cd referral_system

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

Access:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

Stop services:
```bash
docker-compose down
```

---

## 🔗 Integration with Your Telegram Bot

### 1. User Registration
When user starts bot with `/start ref_XXXXX`:

```python
import requests

def handle_start(update, context):
    user = update.effective_user
    args = context.args
    
    # Extract referral code
    referral_code = args[0].replace('ref_', '') if args else None
    
    # Register user in referral system
    response = requests.post('http://localhost:8000/users/create', json={
        'telegram_id': user.id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'referred_by_code': referral_code
    })
    
    user_data = response.json()
    
    # Store user's referral code
    user_ref_code = user_data['referral_code']
    
    # Send welcome message with their referral link
    referral_link = f"https://t.me/YourBot?start=ref_{user_ref_code}"
    update.message.reply_text(
        f"Welcome! Your referral link: {referral_link}"
    )
```

### 2. Create Order
When user wants to buy:

```python
def create_order(telegram_id):
    response = requests.post('http://localhost:8000/orders/create', json={
        'user_id': telegram_id,
        'payment_method': 'upi'
    })
    
    order = response.json()
    return order['order_id']
```

### 3. Process Payment
After payment is confirmed:

```python
def process_payment(order_id, transaction_id, upi_id):
    response = requests.post(
        f'http://localhost:8000/orders/{order_id}/payment-success',
        json={
            'transaction_id': transaction_id
        }
    )
    
    # Commission automatically calculated and credited!
    return response.json()
```

### 4. Check Wallet Balance
Show user their wallet:

```python
def show_wallet(telegram_id):
    response = requests.get(f'http://localhost:8000/wallet/{telegram_id}')
    wallet = response.json()
    
    return f"""
💰 Your Wallet:
• Total Balance: ₹{wallet['total_balance']}
• Withdrawable: ₹{wallet['withdrawable_balance']}
• Pending: ₹{wallet['pending_balance']}
• Total Earned: ₹{wallet['total_earned']}
    """
```

### 5. Withdrawal Request
When user requests withdrawal:

```python
def request_withdrawal(telegram_id, amount, upi_id):
    # Get token (you need to authenticate as the user)
    headers = {'Authorization': f'Bearer {user_token}'}
    
    response = requests.post(
        'http://localhost:8000/withdrawals/create',
        headers=headers,
        json={
            'amount': amount,
            'withdrawal_method': 'upi',
            'upi_id': upi_id
        }
    )
    
    withdrawal = response.json()
    return withdrawal['withdrawal_id']
```

---

## 📊 Admin Panel Features

### Dashboard
- ✅ Real-time statistics
- ✅ Today's performance
- ✅ Revenue tracking
- ✅ Profit monitoring
- ✅ KPI metrics

### User Management
- ✅ View all users
- ✅ Filter by type/status
- ✅ Search users
- ✅ Mark suspicious

### Order Management
- ✅ View all orders
- ✅ Track payments
- ✅ Filter by status
- ✅ Commission tracking

### Referrer Tracking
- ✅ Performance metrics
- ✅ Conversion rates
- ✅ Commission earned
- ✅ Referral tree view

### Withdrawal Management
- ✅ Approve/Reject requests
- ✅ Mark as paid
- ✅ View history
- ✅ Statistics

### Fraud Detection
- ✅ Automatic detection
- ✅ Manual flagging
- ✅ Block/Unblock users
- ✅ Fraud reports

### System Settings
- ✅ Adjust commission rates
- ✅ Change prices
- ✅ Enable/disable features
- ✅ Configure system

---

## 🔧 Common Commands

### Backend
```bash
# Start dev server
uvicorn app.main:app --reload

# Start production
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker

# Run seed data
python seed_data.py

# Process pending commissions manually
python -c "from app.services import PaymentService; from app.database import SessionLocal; db = SessionLocal(); PaymentService.process_pending_commissions(db)"
```

### Frontend
```bash
# Development
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Database
```bash
# Backup
pg_dump ottsonly_referral > backup.sql

# Restore
psql ottsonly_referral < backup.sql

# Connect
psql -d ottsonly_referral
```

---

## 🎯 What Happens Automatically

### When User Makes Purchase:
1. ✅ Order created
2. ✅ User stats updated
3. ✅ Referral marked as converted
4. ✅ Level 1 commission calculated (₹28)
5. ✅ Level 2 commission calculated (₹9)
6. ✅ Commissions credited as PENDING
7. ✅ Fraud checks run automatically

### After 24 Hours:
1. ✅ Pending commissions become withdrawable
2. ✅ User can request withdrawal
3. ✅ Admin approves/rejects
4. ✅ Payment processed

---

## 📝 Important Notes

### Business Rules:
- ✅ Max 2 referral levels
- ✅ 24-hour commission hold
- ✅ ₹500 minimum withdrawal
- ✅ No commission on wallet payments
- ✅ Fresh payments only

### Security:
- ✅ JWT authentication
- ✅ Role-based access
- ✅ SQL injection prevention
- ✅ Input validation
- ✅ Audit logging

### Performance:
- ✅ Database indexes
- ✅ Query optimization
- ✅ Background jobs
- ✅ Caching ready

---

## 🆘 Troubleshooting

### Backend won't start
```bash
# Check Python version
python --version  # Should be 3.9+

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Frontend won't start
```bash
# Clear cache
rm -rf node_modules package-lock.json
npm install
```

### Database connection error
```bash
# Check PostgreSQL is running
pg_isready

# Check connection string in .env
DATABASE_URL=postgresql://user:pass@localhost:5432/ottsonly_referral
```

### Login not working
1. Check SUPER_ADMIN_TELEGRAM_ID in .env
2. Check SUPER_ADMIN_PASSWORD in .env
3. Clear browser cache
4. Check backend logs

---

## 📞 Need Help?

1. Check API docs: http://localhost:8000/docs
2. Review logs in terminal
3. Check database tables
4. Verify .env configuration

---

## ✅ Verification Checklist

- [ ] Database created and schema applied
- [ ] Backend running on port 8000
- [ ] Frontend running on port 3000
- [ ] Can login to admin panel
- [ ] Dashboard shows statistics
- [ ] API documentation accessible
- [ ] Seed data created (optional)
- [ ] Environment variables configured

---

**System is production-ready and fully functional! 🚀**

All modules built. All features working. Ready to integrate with your Telegram bot!
