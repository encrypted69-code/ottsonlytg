"""
EXAMPLE: HOW TO REPLACE JSON WITH SUPABASE
===========================================

This file shows side-by-side comparisons of old JSON code vs new Supabase code.
Use this as a reference when updating your handlers.
"""

# =====================================================
# EXAMPLE 1: GET USER
# =====================================================

# ❌ OLD (json_utils.py)
from utils.json_utils import get_user

user = get_user(telegram_id)

# ✅ NEW (supabase_db.py)
from utils.supabase_db import get_user

user = get_user(telegram_id)
# ^ Same function signature! No code change needed for this one!


# =====================================================
# EXAMPLE 2: CREATE USER
# =====================================================

# ❌ OLD
from utils.json_utils import create_user_if_not_exists

user = create_user_if_not_exists(telegram_id, name, referred_by)

# ✅ NEW
from utils.supabase_db import create_user_if_not_exists

user = create_user_if_not_exists(telegram_id, name, referred_by)
# ^ Also the same! Backward compatible!


# =====================================================
# EXAMPLE 3: UPDATE WALLET
# =====================================================

# ❌ OLD
from utils.json_utils import add_wallet

add_wallet(telegram_id, amount)

# ✅ NEW
from utils.supabase_db import update_wallet

update_wallet(telegram_id, amount, "add")


# =====================================================
# EXAMPLE 4: DEDUCT WALLET
# =====================================================

# ❌ OLD
from utils.json_utils import deduct_wallet

success = deduct_wallet(telegram_id, amount)

# ✅ NEW
from utils.supabase_db import deduct_wallet

success = deduct_wallet(telegram_id, amount)
# ^ Same signature!


# =====================================================
# EXAMPLE 5: GET WALLET BALANCE
# =====================================================

# ❌ OLD
from utils.json_utils import get_wallet_balance

balance = get_wallet_balance(telegram_id)

# ✅ NEW
from utils.supabase_db import get_wallet_balance

balance = get_wallet_balance(telegram_id)
# ^ No change needed!


# =====================================================
# EXAMPLE 6: ADD SUBSCRIPTION
# =====================================================

# ❌ OLD
from utils.json_utils import add_subscription

add_subscription(telegram_id, plan_key)

# ✅ NEW
from utils.supabase_db import add_subscription

add_subscription(telegram_id, plan_key, credential="email:pass")


# =====================================================
# EXAMPLE 7: ADD TRANSACTION
# =====================================================

# ❌ OLD
from utils.json_utils import add_transaction

add_transaction(telegram_id, description, amount)

# ✅ NEW
from utils.supabase_db import create_transaction

create_transaction(telegram_id, description, amount, "credit")


# =====================================================
# EXAMPLE 8: GET PLAN
# =====================================================

# ❌ OLD
from utils.db_utils import get_plan

plan = get_plan(plan_key)

# ✅ NEW
from utils.supabase_db import get_plan

plan = get_plan(plan_key)
# ^ Same function!


# =====================================================
# EXAMPLE 9: GET STOCK/CREDENTIAL
# =====================================================

# ❌ OLD
from utils.db_utils import get_unused_credential

credential = get_unused_credential(plan_key)

# ✅ NEW
from utils.supabase_db import get_unused_credential

credential = get_unused_credential(plan_key)
# ^ No change needed!


# =====================================================
# EXAMPLE 10: MARK CREDENTIAL USED
# =====================================================

# ❌ OLD
from utils.db_utils import mark_credential_used

mark_credential_used(plan_key, credential, telegram_id)

# ✅ NEW
from utils.supabase_db import mark_credential_used

mark_credential_used(plan_key, credential, telegram_id)
# ^ Same!


# =====================================================
# EXAMPLE 11: COMPLETE HANDLER UPDATE
# =====================================================

# ❌ OLD start_handler.py
"""
from utils.json_utils import (
    create_user_if_not_exists,
    get_wallet_balance,
    add_wallet
)
from utils.db_utils import get_plan
"""

# ✅ NEW start_handler.py
"""
from utils.supabase_db import (
    create_user_if_not_exists,
    get_wallet_balance,
    update_wallet,
    get_plan
)
"""


# =====================================================
# EXAMPLE 12: PAYMENT HANDLER
# =====================================================

# ❌ OLD payment_handler.py
"""
from utils.json_utils import (
    get_user,
    add_wallet,
    add_transaction,
    is_payment_processed,
    mark_payment_processed
)

async def handle_payment(payment_id, amount, telegram_id):
    if is_payment_processed(telegram_id, payment_id):
        return
    
    add_wallet(telegram_id, amount)
    add_transaction(telegram_id, "Payment received", amount)
    mark_payment_processed(telegram_id, payment_id)
"""

# ✅ NEW payment_handler.py
"""
from utils.supabase_db import (
    get_user,
    add_wallet_transaction,  # Combined function!
    is_payment_processed,
    mark_payment_processed
)

async def handle_payment(payment_id, amount, telegram_id):
    if is_payment_processed(telegram_id, payment_id):
        return
    
    # This does both: adds to wallet AND creates transaction
    add_wallet_transaction(telegram_id, amount, "Payment received")
    mark_payment_processed(telegram_id, payment_id)
"""


# =====================================================
# EXAMPLE 13: ADMIN GET ALL USERS
# =====================================================

# ❌ OLD
"""
import json

def _read_all():
    with open('data/users.json', 'r') as f:
        return json.load(f)

users = _read_all()
total_users = len(users)
"""

# ✅ NEW
"""
from utils.supabase_db import get_all_users, get_total_users_count

users = get_all_users()
total_users = get_total_users_count()
"""


# =====================================================
# IMPORTANT NOTES
# =====================================================

"""
1. IMPORT CHANGES:
   - Replace: from utils.json_utils → from utils.supabase_db
   - Replace: from utils.db_utils → from utils.supabase_db

2. FUNCTION NAME CHANGES:
   - add_wallet() → update_wallet(user_id, amount, "add")
   - add_transaction() → create_transaction()
   
3. NO CHANGES NEEDED FOR:
   - get_user()
   - create_user_if_not_exists()
   - get_wallet_balance()
   - deduct_wallet()
   - get_plan()
   - get_unused_credential()
   - mark_credential_used()

4. COMBINED FUNCTIONS:
   - add_wallet_transaction() → Does wallet update + transaction in one call

5. ASYNC/AWAIT:
   - Supabase functions are synchronous
   - Can be called from async handlers (they're blocking but fast)
   - For production, consider async wrappers if needed

6. ERROR HANDLING:
   - All functions return None/False on error
   - Check return values before proceeding
   - Errors are logged automatically

7. TESTING:
   - Test each handler after updating
   - Verify data in Supabase Dashboard
   - Check bot logs for errors
"""


# =====================================================
# QUICK REPLACEMENT GUIDE
# =====================================================

"""
Find and replace in all handler files:

1. from utils.json_utils import
   → from utils.supabase_db import

2. from utils.db_utils import
   → from utils.supabase_db import

3. add_wallet(
   → update_wallet(

4. add_transaction(
   → create_transaction(

Then manually verify each file for correct function signatures.
"""
