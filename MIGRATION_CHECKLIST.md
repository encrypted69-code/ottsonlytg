# =====================================================
# SUPABASE MIGRATION CHECKLIST
# =====================================================

## PHASE 1: SETUP ✅
- [ ] Create Supabase project at https://supabase.com
- [ ] Copy project URL and service_role key
- [ ] Copy `.env.example` to `.env`
- [ ] Add Supabase credentials to `.env`
- [ ] Install dependencies: `pip install -r requirements.txt`

## PHASE 2: DATABASE SETUP ✅
- [ ] Open Supabase SQL Editor
- [ ] Paste and run `supabase_schema.sql` completely
- [ ] Verify all tables created (users, plans, stocks, transactions, subscriptions)
- [ ] Check indexes and triggers are active

## PHASE 3: DATA MIGRATION ✅
- [ ] **BACKUP JSON FILES FIRST** (copy `data/` folder to `data_backup/`)
- [ ] Run migration script: `python migrate_to_supabase.py`
- [ ] Verify migration counts match JSON records
- [ ] Check data in Supabase Dashboard → Table Editor
- [ ] Verify relationships (users → subscriptions, plans → stocks)

## PHASE 4: CODE REFACTORING ✅
- [ ] Replace imports in handlers:
  ```python
  # OLD
  from utils.json_utils import get_user, create_user_if_not_exists
  
  # NEW
  from utils.supabase_db import get_user, create_user_if_not_exists
  ```

- [ ] Update handler files:
  - [ ] `handlers/start_handler.py`
  - [ ] `handlers/wallet_handler.py`
  - [ ] `handlers/payment_handler.py`
  - [ ] `handlers/profile_handler.py`
  - [ ] `handlers/ott_handler.py`
  - [ ] `handlers/admin_handler.py`
  - [ ] `handlers/refer_handler.py`

## PHASE 5: TESTING ✅
- [ ] Start bot: `python main.py`
- [ ] Test `/start` command
- [ ] Test user creation
- [ ] Test wallet balance display
- [ ] Test adding funds
- [ ] Test buying OTT plans
- [ ] Test admin commands
- [ ] Test referral system
- [ ] Verify no errors in console

## PHASE 6: PRODUCTION DEPLOYMENT ✅
- [ ] Run bot for 24 hours in test mode
- [ ] Monitor Supabase logs
- [ ] Check for any database errors
- [ ] Verify all features working
- [ ] Test with real users

## PHASE 7: CLEANUP (ONLY AFTER FULL TESTING) ⚠️
- [ ] Confirm bot stable for 3+ days
- [ ] Create final backup of JSON files
- [ ] Archive JSON files (move to `archive/` folder)
- [ ] Remove old utility files:
  - [ ] `utils/json_utils.py` (keep as reference)
  - [ ] `utils/db_utils.py` (old stock management)
- [ ] Remove JSON file references from settings
- [ ] Update README with Supabase setup instructions

## ROLLBACK PLAN 🔄
If something goes wrong:
1. Stop the bot
2. Restore JSON files from `data_backup/`
3. Revert code changes (use git)
4. Restart bot with old JSON system
5. Debug issues before retrying

## MONITORING 📊
After migration, monitor:
- Database connection stability
- Query performance
- Error logs in Supabase Dashboard
- Bot response times
- User complaints/issues

## SUPPORT CONTACTS
- Supabase Docs: https://supabase.com/docs
- Supabase Discord: https://discord.supabase.com
- Supabase Status: https://status.supabase.com

---

**⚠️ CRITICAL REMINDERS:**
1. Never delete JSON files until 100% stable
2. Always have backups before deployment
3. Test thoroughly in non-production first
4. Keep `.env` file secure and never commit it
5. Use service_role key only in backend code

---

**✅ MIGRATION COMPLETE WHEN:**
- All tests pass ✓
- No database errors for 3 days ✓
- All features working ✓
- Users reporting no issues ✓
- JSON files safely archived ✓
