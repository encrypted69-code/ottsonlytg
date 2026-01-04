# 📊 CENTRALIZED LOGGING SYSTEM DOCUMENTATION

## Overview
Production-ready logging system for your Telegram OTT bot with real-time notifications to admin channel and optional database storage.

---

## ✅ Features

1. **Real-time Telegram Notifications** - All events sent to your logs channel
2. **Structured Event Types** - Dedicated functions for each event category
3. **Consistent Formatting** - Mobile-friendly, emoji-rich messages
4. **Database Logging** (Optional) - Store logs in Supabase for analytics
5. **Error Handling** - Non-blocking, fail-safe logging
6. **Security** - No credential leakage

---

## 📁 Files Created

- `utils/log_utils.py` - Main logging functions
- `utils/supabase_db.py` - Database logging functions (added)
- `setup_logs_table.py` - Database table setup script
- `LOGGING_DOCUMENTATION.md` - This file

---

## 🚀 Quick Start

### 1. Verify Configuration

Check `config/settings.py`:
```python
LOG_CHANNEL_ID = -4758912978  # Your admin logs channel
```

### 2. Import Logging Functions

In your handler files:
```python
from utils.log_utils import (
    log_user_start,
    log_payment_success,
    log_purchase_success,
    log_error
)
```

### 3. Use in Your Code

```python
# Example: User starts bot
await log_user_start(
    user_id=message.from_user.id,
    username=message.from_user.username,
    is_new=True
)

# Example: Payment successful
await log_payment_success(
    user_id=user_id,
    username=username,
    amount=99,
    order_id="ORDER12345",
    utr="UTR123456"
)
```

---

## 📋 Available Functions

### USER EVENTS

#### `log_user_start(user_id, username, is_new=False)`
Log when user starts/restarts bot.
```python
await log_user_start(123456789, "john_doe", is_new=True)
```

#### `log_user_blocked(user_id, username)`
Log when user blocks the bot (if detectable).
```python
await log_user_blocked(123456789, "john_doe")
```

---

### PAYMENT EVENTS

#### `log_payment_pending(user_id, username, amount, order_id)`
Log QR generation and pending payment.
```python
await log_payment_pending(123456789, "john_doe", 99, "ORDER123")
```

#### `log_payment_success(user_id, username, amount, order_id, utr=None)`
Log successful payment.
```python
await log_payment_success(123456789, "john_doe", 99, "ORDER123", "UTR456")
```

#### `log_payment_failed(user_id, username, amount, order_id, reason)`
Log failed payment.
```python
await log_payment_failed(123456789, "john_doe", 99, "ORDER123", "Invalid UTR")
```

#### `log_payment_timeout(user_id, username, amount, order_id)`
Log payment expiration.
```python
await log_payment_timeout(123456789, "john_doe", 99, "ORDER123")
```

---

### PURCHASE EVENTS

#### `log_purchase_success(user_id, username, plan_name, price, order_id, new_balance)`
Log successful OTT purchase.
```python
await log_purchase_success(
    user_id=123456789,
    username="john_doe",
    plan_name="Netflix 4K",
    price=99,
    order_id="NETFLIX789",
    new_balance=50
)
```

#### `log_purchase_failed(user_id, username, plan_name, reason)`
Log failed purchase.
```python
await log_purchase_failed(123456789, "john_doe", "Netflix 4K", "Insufficient balance")
```

#### `log_stock_unavailable(user_id, username, plan_name)`
Log out-of-stock situations.
```python
await log_stock_unavailable(123456789, "john_doe", "Prime Video")
```

#### `log_combo_partial_failure(user_id, username, allocated, missing)`
Log combo plan partial allocations.
```python
await log_combo_partial_failure(
    123456789,
    "john_doe",
    allocated=["netflix_4k", "prime_video"],
    missing=["pornhub"]
)
```

---

### QR EVENTS

#### `log_qr_generated(user_id, username, amount, order_id)`
```python
await log_qr_generated(123456789, "john_doe", 99, "ORDER123")
```

#### `log_qr_reused(user_id, username, order_id)`
```python
await log_qr_reused(123456789, "john_doe", "ORDER123")
```

---

### ERROR EVENTS

#### `log_error(error_type, details, user_id=None, username=None)`
Log system errors.
```python
await log_error(
    error_type="API Error",
    details="Payment verification API timeout",
    user_id=123456789,
    username="john_doe"
)
```

#### `log_database_error(operation, details, user_id=None)`
Log database-specific errors.
```python
await log_database_error(
    operation="insert_transaction",
    details="Foreign key constraint failed",
    user_id=123456789
)
```

---

### WALLET EVENTS

#### `log_wallet_credit(user_id, username, amount, new_balance, source)`
```python
await log_wallet_credit(123456789, "john_doe", 100, 150, "Payment")
```

#### `log_wallet_debit(user_id, username, amount, new_balance, reason)`
```python
await log_wallet_debit(123456789, "john_doe", 99, 51, "Netflix Purchase")
```

---

### REFERRAL EVENTS

#### `log_referral(referrer_id, referrer_username, new_user_id, new_user_username)`
```python
await log_referral(111111, "referrer", 222222, "new_user")
```

---

## 💾 Database Logging (Optional)

### Setup

1. Create logs table:
```bash
python setup_logs_table.py
```

Or run SQL manually in Supabase SQL Editor (see script).

2. Import database logging:
```python
from utils.supabase_db import store_log_in_db, get_recent_logs
```

3. Store logs:
```python
# Store in database along with Telegram notification
await log_payment_success(...)  # Sends to Telegram
store_log_in_db(
    event_type="PAYMENT_SUCCESS",
    telegram_id=user_id,
    username=username,
    details={"amount": 99, "order_id": "ORDER123"},
    message="Payment successful"
)
```

### Query Logs

```python
# Get recent logs
recent = get_recent_logs(limit=100)

# Get logs by event type
payments = get_recent_logs(limit=50, event_type="PAYMENT_SUCCESS")

# Get user activity
user_logs = get_user_activity_logs(telegram_id=123456789, limit=20)
```

---

## 🔧 Integration Examples

### Example 1: Start Handler

```python
# handlers/start_handler.py
from utils.log_utils import log_user_start
from utils.supabase_db import create_user_if_not_exists

@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username
    
    # Create user
    user = create_user_if_not_exists(user_id, message.from_user.full_name)
    is_new = user.get("is_new", False)
    
    # Log the event
    await log_user_start(user_id, username, is_new=is_new)
    
    # Send welcome message
    await message.answer("Welcome!")
```

### Example 2: Payment Handler

```python
# handlers/payment_handler.py
from utils.log_utils import (
    log_qr_generated,
    log_payment_pending,
    log_payment_success,
    log_payment_failed
)

async def generate_qr(user_id, username, amount):
    order_id = generate_order_id()
    
    # Log QR generation
    await log_qr_generated(user_id, username, amount, order_id)
    await log_payment_pending(user_id, username, amount, order_id)
    
    # Generate QR code
    qr_code = create_qr(amount, order_id)
    return qr_code, order_id

async def verify_payment(user_id, username, amount, order_id, utr):
    try:
        # Verify payment
        result = await verify_utr(utr)
        
        if result["success"]:
            # Update wallet
            new_balance = update_wallet(user_id, amount)
            
            # Log success
            await log_payment_success(user_id, username, amount, order_id, utr)
            return True
        else:
            # Log failure
            await log_payment_failed(user_id, username, amount, order_id, result["error"])
            return False
            
    except Exception as e:
        await log_error("Payment Verification", str(e), user_id, username)
        return False
```

### Example 3: Purchase Handler

```python
# handlers/ott_handler.py
from utils.log_utils import (
    log_purchase_success,
    log_purchase_failed,
    log_stock_unavailable
)

async def purchase_ott(user_id, username, plan_key):
    plan = get_plan(plan_key)
    
    # Check stock
    credential = get_unused_credential(plan_key)
    if not credential:
        await log_stock_unavailable(user_id, username, plan["name"])
        return False
    
    # Check balance
    balance = get_wallet_balance(user_id)
    if balance < plan["price"]:
        await log_purchase_failed(user_id, username, plan["name"], "Insufficient balance")
        return False
    
    # Deduct wallet
    deduct_wallet(user_id, plan["price"])
    mark_credential_used(plan_key, credential, user_id)
    
    # Generate order ID
    order_id = f"{plan_key.upper()}{random.randint(1000, 9999)}"
    
    # Log success
    new_balance = get_wallet_balance(user_id)
    await log_purchase_success(
        user_id, username,
        plan["name"], plan["price"],
        order_id, new_balance
    )
    
    return True
```

---

## 🛡️ Security Best Practices

### ✅ DO:
- Log user IDs and usernames
- Log transaction amounts and order IDs
- Log timestamps automatically
- Use consistent formatting

### ❌ DON'T:
- Log passwords or credentials
- Log sensitive API keys
- Log full credit card numbers
- Log personal identifiable information unnecessarily

### Safe Logging Examples:

```python
# ✅ GOOD - Generic credential reference
await log_purchase_success(..., order_id="NETFLIX789", ...)

# ❌ BAD - Logging actual credentials
await send_log(f"Credential: email@example.com:password123")  # NEVER DO THIS

# ✅ GOOD - Masked UTR
utr_masked = utr[:4] + "****" + utr[-4:] if len(utr) > 8 else "****"

# ✅ GOOD - Error without sensitive data
await log_error("Database Error", "Connection timeout")
```

---

## 📊 Log Message Formats

All logs follow this structure:

```
[EMOJI] *EVENT NAME*

User: @username (ID: `123456789`)
[Event-specific fields]
Time: `DD/MM/YYYY HH:MM:SS`
```

Examples:

**Payment Success:**
```
✅ *PAYMENT SUCCESSFUL*

User: @john_doe (ID: `123456789`)
Amount: ₹99
Order ID: `ORDER123`
UTR: `UTR456789`
Time: `04/01/2026 18:30:45`
```

**Purchase Failed:**
```
❌ *PURCHASE FAILED*

User: @john_doe (ID: `123456789`)
Plan: Netflix 4K
Reason: Stock unavailable
Time: `04/01/2026 18:35:12`
```

---

## 🔍 Monitoring & Analytics

### View Real-time Logs
Check your Telegram logs channel: `-4758912978`

### Query Database Logs (if enabled)
```python
# Get payment statistics
from utils.supabase_db import get_recent_logs

payment_logs = get_recent_logs(limit=1000, event_type="PAYMENT_SUCCESS")
total_revenue = sum(log["details"]["amount"] for log in payment_logs)
print(f"Total Revenue: ₹{total_revenue}")
```

---

## 🐛 Troubleshooting

### Logs not appearing in channel?

1. Check channel ID in `config/settings.py`:
   ```python
   LOG_CHANNEL_ID = -4758912978
   ```

2. Ensure bot is admin in the channel

3. Test logging:
   ```python
   from utils.log_utils import send_log
   await send_log("🧪 *Test Message*\n\nIf you see this, logging works!")
   ```

### Database logs not storing?

1. Create logs table:
   ```bash
   python setup_logs_table.py
   ```

2. Check Supabase credentials in `.env`

---

## 📈 Next Steps

1. **Review existing handlers** and add logging calls
2. **Test each log type** to ensure proper formatting
3. **Monitor logs channel** for any issues
4. **Optionally enable database logging** for analytics
5. **Set up alerts** for critical errors

---

## 🎯 Summary

You now have a complete, production-ready logging system:

- ✅ Real-time Telegram notifications
- ✅ Structured event types
- ✅ Consistent, mobile-friendly formatting
- ✅ Optional database storage
- ✅ Non-blocking, fail-safe execution
- ✅ Security-first approach

**Next:** Integrate logging into your handlers and start monitoring! 🚀
