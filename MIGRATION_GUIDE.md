# 🚀 SUPABASE MIGRATION - COMPLETE GUIDE

## 📋 Overview

This migration moves your Telegram OTT bot from local JSON storage to **Supabase PostgreSQL** - a production-ready, scalable cloud database.

---

## 🗂️ Files Created

### 1. **supabase_schema.sql** 
Complete database schema with:
- `users` table (telegram_id, wallet, referrals, etc.)
- `plans` table (OTT plan configurations)
- `stocks` table (credentials inventory)
- `transactions` table (payment history)
- `subscriptions` table (user purchases)
- Indexes, foreign keys, triggers

### 2. **migrate_to_supabase.py**
Automated migration script that:
- Reads all JSON files
- Imports data to Supabase
- Prevents duplicates
- Logs success/failures
- Verifies migration

### 3. **utils/supabase_db.py**
New database layer with functions:
- `get_user()`, `create_user()`
- `update_wallet()`, `deduct_wallet()`
- `get_plan()`, `create_plan()`
- `add_stock()`, `get_unused_credential()`
- `add_subscription()`, `create_transaction()`
- And more...

### 4. **MIGRATION_CHECKLIST.md**
Step-by-step checklist for safe migration

### 5. **MIGRATION_EXAMPLES.py**
Code examples showing old vs new syntax

### 6. **.env.example**
Template for Supabase credentials

---

## 🔧 Quick Start (5 Steps)

### Step 1: Setup Supabase
```bash
1. Go to https://supabase.com
2. Create new project
3. Copy your project URL
4. Copy your service_role key (Settings → API)
```

### Step 2: Configure Environment
```bash
# Copy example file
cp .env.example .env

# Edit .env and add your credentials:
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here
```

### Step 3: Install Dependencies
```bash
pip install supabase python-dotenv
```

### Step 4: Create Database Schema
```bash
1. Open Supabase Dashboard → SQL Editor
2. Copy entire content of supabase_schema.sql
3. Paste and click "Run"
4. Verify all tables created (check Table Editor)
```

### Step 5: Run Migration
```bash
# BACKUP FIRST!
cp -r data/ data_backup/

# Run migration
python migrate_to_supabase.py

# Verify in Supabase Dashboard
```

---

## 📝 Updating Your Code

### Simple Import Changes

Most functions have the **same name and signature**, so you only need to change imports:

```python
# OLD
from utils.json_utils import get_user, create_user_if_not_exists
from utils.db_utils import get_plan

# NEW  
from utils.supabase_db import get_user, create_user_if_not_exists, get_plan
```

### Function Mapping

| Old Function | New Function | Notes |
|-------------|-------------|-------|
| `get_user()` | `get_user()` | ✅ Same |
| `create_user_if_not_exists()` | `create_user_if_not_exists()` | ✅ Same |
| `get_wallet_balance()` | `get_wallet_balance()` | ✅ Same |
| `deduct_wallet()` | `deduct_wallet()` | ✅ Same |
| `add_wallet()` | `update_wallet(id, amt, "add")` | Changed |
| `add_transaction()` | `create_transaction()` | Renamed |
| `get_plan()` | `get_plan()` | ✅ Same |
| `get_unused_credential()` | `get_unused_credential()` | ✅ Same |
| `mark_credential_used()` | `mark_credential_used()` | ✅ Same |

### Files to Update

Update these handler files (just change the imports at the top):

1. ✅ `handlers/start_handler.py`
2. ✅ `handlers/wallet_handler.py`
3. ✅ `handlers/payment_handler.py`
4. ✅ `handlers/profile_handler.py`
5. ✅ `handlers/ott_handler.py`
6. ✅ `handlers/admin_handler.py`
7. ✅ `handlers/refer_handler.py`

See `MIGRATION_EXAMPLES.py` for detailed code examples.

---

## ✅ Testing Checklist

After migration, test these features:

- [ ] `/start` - User creation
- [ ] Wallet balance display
- [ ] Add funds
- [ ] Buy OTT plan
- [ ] View profile
- [ ] Referral links
- [ ] Admin commands
- [ ] Transaction history

---

## 🔒 Security Best Practices

1. **Never commit .env file**
   ```bash
   echo ".env" >> .gitignore
   ```

2. **Use service_role key only in backend**
   - Never expose in frontend/client code
   - Keep .env file secure

3. **Enable Row Level Security (RLS) in Supabase**
   - Go to Table Editor → Select table → Enable RLS
   - Add policies for security

4. **Backup regularly**
   - Use Supabase built-in backups
   - Keep JSON backups for 30 days

---

## 📊 Benefits of Supabase

### Before (JSON)
❌ Single point of failure  
❌ No concurrent access  
❌ Manual backups  
❌ No query optimization  
❌ Risk of data corruption  
❌ Limited to one server  

### After (Supabase)
✅ Automatic backups  
✅ Handles 1000s of concurrent users  
✅ PostgreSQL reliability  
✅ Built-in analytics  
✅ Real-time capabilities  
✅ Scalable infrastructure  

---

## 🆘 Troubleshooting

### Error: "Missing Supabase credentials"
**Solution:** Check your `.env` file has correct URL and key

### Error: "relation does not exist"
**Solution:** Run `supabase_schema.sql` first in SQL Editor

### Error: "duplicate key value"
**Solution:** Migration ran twice. Clear tables and re-run

### Migration shows 0 records
**Solution:** Check JSON file paths are correct

### Bot not connecting to database
**Solution:** Verify Supabase project is not paused (free tier pauses after inactivity)

---

## 🔄 Rollback Plan

If something goes wrong:

```bash
1. Stop the bot
2. Restore from backup:
   cp -r data_backup/* data/
3. Revert code changes (git reset)
4. Restart bot
5. Debug the issue
6. Try migration again
```

---

## 📞 Support

- **Supabase Docs:** https://supabase.com/docs
- **Supabase Discord:** https://discord.supabase.com
- **Database Issues:** Check Supabase Dashboard → Logs

---

## 🎯 Next Steps

After successful migration:

1. ✅ Monitor bot for 3-7 days
2. ✅ Check Supabase logs daily
3. ✅ Verify no user complaints
4. ✅ Archive JSON files (don't delete yet!)
5. ✅ Update documentation
6. ✅ Set up monitoring alerts
7. ✅ Enable RLS policies
8. ✅ Configure automatic backups

---

## 🏆 Production Checklist

Before going live:

- [ ] All features tested
- [ ] No console errors
- [ ] Database queries optimized
- [ ] Backups configured
- [ ] Security policies enabled
- [ ] Error logging setup
- [ ] Monitoring in place
- [ ] Team trained on new system

---

## 📈 Performance Tips

1. **Use connection pooling** (built-in with supabase-py)
2. **Add indexes** on frequently queried fields (already included)
3. **Monitor query performance** in Supabase Dashboard
4. **Cache frequent queries** if needed
5. **Use batch operations** for bulk updates

---

## 🎉 Congratulations!

You now have a production-ready, scalable database for your Telegram bot!

**Your bot can now:**
- Handle thousands of concurrent users
- Scale automatically
- Recover from failures
- Provide real-time analytics
- Support multiple regions

**Happy Coding! 🚀**

---

*For questions or issues, refer to MIGRATION_CHECKLIST.md and MIGRATION_EXAMPLES.py*
