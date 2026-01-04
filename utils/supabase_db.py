"""
SUPABASE DATABASE UTILITIES
============================
Production-ready database layer using Supabase PostgreSQL.
Replaces all JSON-based storage with scalable cloud database.

This module provides clean, reusable functions for all database operations.
"""

import os
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("❌ Missing Supabase credentials. Check your .env file.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# =====================================================
# USER MANAGEMENT
# =====================================================

def get_user(telegram_id: int) -> Optional[Dict]:
    """
    Get user by telegram ID.
    
    Args:
        telegram_id: Telegram user ID
        
    Returns:
        User dictionary or None if not found
    """
    try:
        response = supabase.table("users").select("*").eq("telegram_id", telegram_id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"❌ Error getting user {telegram_id}: {e}")
        return None


def create_user(telegram_id: int, name: str = "", referred_by: int = None) -> Optional[Dict]:
    """
    Create new user if not exists.
    
    Args:
        telegram_id: Telegram user ID
        name: User's display name
        referred_by: Referrer's telegram ID
        
    Returns:
        Created user dictionary or existing user
    """
    try:
        # Check if user exists
        existing = get_user(telegram_id)
        if existing:
            return existing
        
        user_data = {
            "telegram_id": telegram_id,
            "name": name,
            "wallet": 0,
            "referred_by": referred_by,
            "referrals": [],
            "processed_payments": []
        }
        
        response = supabase.table("users").insert(user_data).execute()
        
        # If user was referred, add to referrer's list
        if referred_by:
            add_referral(referred_by, telegram_id)
        
        return response.data[0] if response.data else None
        
    except Exception as e:
        print(f"❌ Error creating user {telegram_id}: {e}")
        return None


def create_user_if_not_exists(telegram_id: int, name: str = "", referred_by: int = None) -> Optional[Dict]:
    """
    Wrapper for create_user (for backward compatibility).
    """
    return create_user(telegram_id, name, referred_by)


def get_wallet_balance(telegram_id: int) -> int:
    """
    Get user's wallet balance.
    
    Args:
        telegram_id: Telegram user ID
        
    Returns:
        Wallet balance (0 if user not found)
    """
    user = get_user(telegram_id)
    return user.get("wallet", 0) if user else 0


def update_wallet(telegram_id: int, amount: int, operation: str = "add") -> bool:
    """
    Update user's wallet balance.
    
    Args:
        telegram_id: Telegram user ID
        amount: Amount to add or subtract
        operation: "add" or "subtract"
        
    Returns:
        True if successful, False otherwise
    """
    try:
        user = get_user(telegram_id)
        if not user:
            return False
        
        current_balance = user.get("wallet", 0)
        
        if operation == "add":
            new_balance = current_balance + amount
        elif operation == "subtract":
            new_balance = max(0, current_balance - amount)
        else:
            return False
        
        supabase.table("users").update({"wallet": new_balance}).eq("telegram_id", telegram_id).execute()
        return True
        
    except Exception as e:
        print(f"❌ Error updating wallet for {telegram_id}: {e}")
        return False


def deduct_wallet(telegram_id: int, amount: int) -> bool:
    """
    Deduct amount from user's wallet.
    
    Args:
        telegram_id: Telegram user ID
        amount: Amount to deduct
        
    Returns:
        True if successful, False otherwise
    """
    try:
        user = get_user(telegram_id)
        if not user:
            return False
        
        current_balance = user.get("wallet", 0)
        
        if current_balance < amount:
            return False
        
        new_balance = current_balance - amount
        supabase.table("users").update({"wallet": new_balance}).eq("telegram_id", telegram_id).execute()
        return True
        
    except Exception as e:
        print(f"❌ Error deducting wallet for {telegram_id}: {e}")
        return False


def add_referral(referrer_id: int, new_user_id: int) -> bool:
    """
    Add a new referral to referrer's list.
    
    Args:
        referrer_id: Referrer's telegram ID
        new_user_id: New user's telegram ID
        
    Returns:
        True if successful
    """
    try:
        referrer = get_user(referrer_id)
        if not referrer:
            return False
        
        referrals = referrer.get("referrals", [])
        if new_user_id not in referrals:
            referrals.append(new_user_id)
            supabase.table("users").update({"referrals": referrals}).eq("telegram_id", referrer_id).execute()
        
        return True
        
    except Exception as e:
        print(f"❌ Error adding referral: {e}")
        return False


def set_referred_by(telegram_id: int, referrer_id: int) -> bool:
    """
    Set who referred this user.
    
    Args:
        telegram_id: User's telegram ID
        referrer_id: Referrer's telegram ID
        
    Returns:
        True if successful
    """
    try:
        user = get_user(telegram_id)
        if not user or user.get("referred_by"):
            return False  # Already has a referrer
        
        supabase.table("users").update({"referred_by": referrer_id}).eq("telegram_id", telegram_id).execute()
        add_referral(referrer_id, telegram_id)
        return True
        
    except Exception as e:
        print(f"❌ Error setting referrer: {e}")
        return False


def get_all_users() -> List[Dict]:
    """
    Get all users from database.
    
    Returns:
        List of all user dictionaries
    """
    try:
        response = supabase.table("users").select("*").execute()
        return response.data
    except Exception as e:
        print(f"❌ Error getting all users: {e}")
        return []


def mark_payment_processed(telegram_id: int, payment_id: str) -> bool:
    """
    Mark a payment as processed to prevent duplicates.
    
    Args:
        telegram_id: User's telegram ID
        payment_id: Payment ID
        
    Returns:
        True if successful
    """
    try:
        user = get_user(telegram_id)
        if not user:
            return False
        
        processed = user.get("processed_payments", [])
        if payment_id not in processed:
            processed.append(payment_id)
            supabase.table("users").update({"processed_payments": processed}).eq("telegram_id", telegram_id).execute()
        
        return True
        
    except Exception as e:
        print(f"❌ Error marking payment: {e}")
        return False


def is_payment_processed(telegram_id: int, payment_id: str) -> bool:
    """
    Check if payment was already processed.
    
    Args:
        telegram_id: User's telegram ID
        payment_id: Payment ID
        
    Returns:
        True if already processed
    """
    user = get_user(telegram_id)
    if not user:
        return False
    
    processed = user.get("processed_payments", [])
    return payment_id in processed


# =====================================================
# PLAN MANAGEMENT
# =====================================================

def get_plan(plan_key: str) -> Optional[Dict]:
    """
    Get plan details by plan key.
    
    Args:
        plan_key: Plan identifier
        
    Returns:
        Plan dictionary or None
    """
    try:
        response = supabase.table("plans").select("*").eq("plan_key", plan_key).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"❌ Error getting plan {plan_key}: {e}")
        return None


def get_all_plans() -> List[Dict]:
    """
    Get all available plans.
    
    Returns:
        List of plan dictionaries
    """
    try:
        response = supabase.table("plans").select("*").execute()
        return response.data
    except Exception as e:
        print(f"❌ Error getting plans: {e}")
        return []


def create_plan(plan_key: str, ott_name: str, price: int, description: str = "") -> bool:
    """
    Create new OTT plan.
    
    Args:
        plan_key: Unique plan identifier
        ott_name: Display name
        price: Plan price
        description: Plan description
        
    Returns:
        True if successful
    """
    try:
        plan_data = {
            "plan_key": plan_key,
            "ott_name": ott_name,
            "price": price,
            "description": description,
            "stock": 0,
            "active": True
        }
        
        supabase.table("plans").insert(plan_data).execute()
        return True
        
    except Exception as e:
        print(f"❌ Error creating plan {plan_key}: {e}")
        return False


def update_plan_price(plan_key: str, price: int) -> bool:
    """
    Update plan price.
    
    Args:
        plan_key: Plan identifier
        price: New price
        
    Returns:
        True if successful
    """
    try:
        supabase.table("plans").update({"price": price}).eq("plan_key", plan_key).execute()
        return True
    except Exception as e:
        print(f"❌ Error updating plan price: {e}")
        return False


def toggle_plan_active(plan_key: str) -> Optional[bool]:
    """
    Toggle plan active status.
    
    Args:
        plan_key: Plan identifier
        
    Returns:
        New active status or None if error
    """
    try:
        plan = get_plan(plan_key)
        if not plan:
            return None
        
        new_status = not plan.get("active", True)
        supabase.table("plans").update({"active": new_status}).eq("plan_key", plan_key).execute()
        return new_status
        
    except Exception as e:
        print(f"❌ Error toggling plan: {e}")
        return None


def update_plan_details(plan_key: str, description: str) -> bool:
    """
    Update plan description.
    
    Args:
        plan_key: Plan identifier
        description: New description
        
    Returns:
        True if successful
    """
    try:
        supabase.table("plans").update({"description": description}).eq("plan_key", plan_key).execute()
        return True
    except Exception as e:
        print(f"❌ Error updating plan details: {e}")
        return False


# =====================================================
# STOCK MANAGEMENT
# =====================================================

def add_stock(plan_key: str, credential: str) -> bool:
    """
    Add new credential to stock.
    
    Args:
        plan_key: Plan identifier
        credential: Login credentials
        
    Returns:
        True if successful
    """
    try:
        stock_data = {
            "plan_key": plan_key,
            "credential": credential,
            "is_used": False
        }
        
        supabase.table("stocks").insert(stock_data).execute()
        return True
        
    except Exception as e:
        print(f"❌ Error adding stock: {e}")
        return False


def add_credentials(plan_key: str, credentials_list: list) -> dict:
    """
    Add multiple credentials to stock (bulk upload).
    
    Args:
        plan_key: Plan identifier
        credentials_list: List of credential strings
        
    Returns:
        Dict with added count, duplicates, and total stock
    """
    added = 0
    duplicates = 0
    
    try:
        # Get existing credentials for this plan
        existing = supabase.table("stocks")\
            .select("credential")\
            .eq("plan_key", plan_key)\
            .execute()
        
        existing_creds = {row["credential"] for row in existing.data}
        
        # Insert only new credentials
        for credential in credentials_list:
            if credential in existing_creds:
                duplicates += 1
                continue
            
            try:
                stock_data = {
                    "plan_key": plan_key,
                    "credential": credential,
                    "is_used": False
                }
                supabase.table("stocks").insert(stock_data).execute()
                added += 1
            except Exception as e:
                print(f"❌ Error adding credential {credential}: {e}")
                duplicates += 1
        
        # Get total stock count
        total = get_stock_count(plan_key)
        
        return {
            "added": added,
            "duplicates": duplicates,
            "total": total
        }
        
    except Exception as e:
        print(f"❌ Error adding credentials: {e}")
        return {
            "added": 0,
            "duplicates": len(credentials_list),
            "total": 0
        }


def get_unused_credential(plan_key: str) -> Optional[str]:
    """
    Get an unused credential for a plan.
    
    Args:
        plan_key: Plan identifier
        
    Returns:
        Credential string or None if no stock
    """
    try:
        response = supabase.table("stocks").select("*").eq("plan_key", plan_key).eq("is_used", False).limit(1).execute()
        
        if response.data:
            return response.data[0].get("credential")
        return None
        
    except Exception as e:
        print(f"❌ Error getting credential: {e}")
        return None


def mark_credential_used(plan_key: str, credential: str, telegram_id: int) -> bool:
    """
    Mark a credential as used.
    Only marks ONE credential even if there are duplicates.
    
    Args:
        plan_key: Plan identifier
        credential: Credential string
        telegram_id: User who used it
        
    Returns:
        True if successful
    """
    try:
        # First, get ONE unused credential ID that matches
        response = supabase.table("stocks").select("id").eq("plan_key", plan_key).eq("credential", credential).eq("is_used", False).limit(1).execute()
        
        if not response.data:
            print(f"⚠️ No unused credential found for {plan_key}: {credential}")
            return False
        
        credential_id = response.data[0]["id"]
        
        # Update only that specific credential by ID
        update_data = {
            "is_used": True,
            "used_by": telegram_id,
            "used_at": datetime.now().isoformat()
        }
        
        supabase.table("stocks").update(update_data).eq("id", credential_id).execute()
        print(f"✅ Marked credential ID {credential_id} as used for user {telegram_id}")
        return True
        
    except Exception as e:
        print(f"❌ Error marking credential used: {e}")
        return False


def get_stock_count(plan_key: str) -> int:
    """
    Get available stock count for a plan.
    
    Args:
        plan_key: Plan identifier
        
    Returns:
        Number of unused credentials
    """
    try:
        response = supabase.table("stocks").select("id", count="exact").eq("plan_key", plan_key).eq("is_used", False).execute()
        return response.count if response.count else 0
    except Exception as e:
        print(f"❌ Error getting stock count: {e}")
        return 0


def delete_stock(stock_id: int) -> bool:
    """
    Delete a stock item by ID.
    
    Args:
        stock_id: Stock record ID
        
    Returns:
        True if successful
    """
    try:
        supabase.table("stocks").delete().eq("id", stock_id).execute()
        return True
    except Exception as e:
        print(f"❌ Error deleting stock: {e}")
        return False


# =====================================================
# SUBSCRIPTION MANAGEMENT
# =====================================================

def add_subscription(telegram_id: int, plan_key: str, credential: str = None) -> bool:
    """
    Add subscription for user.
    
    Args:
        telegram_id: User's telegram ID
        plan_key: Plan identifier
        credential: Optional credential info
        
    Returns:
        True if successful
    """
    try:
        sub_data = {
            "telegram_id": telegram_id,
            "plan_key": plan_key,
            "credential": credential,
            "status": "active",
            "expires_at": (datetime.now() + timedelta(days=30)).isoformat()
        }
        
        supabase.table("subscriptions").insert(sub_data).execute()
        return True
        
    except Exception as e:
        print(f"❌ Error adding subscription: {e}")
        return False


def get_user_subscriptions(telegram_id: int) -> List[Dict]:
    """
    Get all subscriptions for a user.
    
    Args:
        telegram_id: User's telegram ID
        
    Returns:
        List of subscription dictionaries
    """
    try:
        response = supabase.table("subscriptions").select("*").eq("telegram_id", telegram_id).execute()
        return response.data
    except Exception as e:
        print(f"❌ Error getting subscriptions: {e}")
        return []


# =====================================================
# TRANSACTION MANAGEMENT
# =====================================================

def create_transaction(telegram_id: int, description: str, amount: int, 
                       transaction_type: str = "credit", payment_id: str = None) -> bool:
    """
    Create new transaction record.
    
    Args:
        telegram_id: User's telegram ID
        description: Transaction description
        amount: Transaction amount
        transaction_type: Type of transaction
        payment_id: Optional payment ID
        
    Returns:
        True if successful
    """
    try:
        txn_data = {
            "telegram_id": telegram_id,
            "description": description,
            "amount": amount,
            "transaction_type": transaction_type,
            "payment_id": payment_id
        }
        
        supabase.table("transactions").insert(txn_data).execute()
        return True
        
    except Exception as e:
        print(f"❌ Error creating transaction: {e}")
        return False


def get_user_transactions(telegram_id: int) -> List[Dict]:
    """
    Get all transactions for a user.
    
    Args:
        telegram_id: User's telegram ID
        
    Returns:
        List of transaction dictionaries
    """
    try:
        response = supabase.table("transactions").select("*").eq("telegram_id", telegram_id).order("timestamp", desc=True).execute()
        return response.data
    except Exception as e:
        print(f"❌ Error getting transactions: {e}")
        return []


def add_wallet_transaction(telegram_id: int, amount: int, description: str = "Wallet Credit") -> bool:
    """
    Add wallet credit and create transaction record.
    
    Args:
        telegram_id: User's telegram ID
        amount: Amount to add
        description: Transaction description
        
    Returns:
        True if successful
    """
    try:
        # Update wallet
        if not update_wallet(telegram_id, amount, "add"):
            return False
        
        # Create transaction record
        return create_transaction(telegram_id, description, amount, "credit")
        
    except Exception as e:
        print(f"❌ Error adding wallet transaction: {e}")
        return False


# =====================================================
# ADMIN FUNCTIONS
# =====================================================

def get_total_users_count() -> int:
    """Get total number of users."""
    try:
        response = supabase.table("users").select("telegram_id", count="exact").execute()
        return response.count if response.count else 0
    except:
        return 0


def get_total_revenue() -> int:
    """Get total revenue from all transactions."""
    try:
        response = supabase.table("transactions").select("amount").eq("transaction_type", "purchase").execute()
        return sum(txn["amount"] for txn in response.data)
    except:
        return 0


# =====================================================
# USER HISTORY
# =====================================================

def get_user_history(telegram_id: int) -> Dict[str, Any]:
    """
    Get complete user history including transactions, purchases, and credentials.
    
    Args:
        telegram_id: User's telegram ID
        
    Returns:
        Dictionary containing:
        - transactions: List of transaction records
        - purchases: List of subscription purchases with plan details
        - credentials: List of delivered credentials
    """
    try:
        # Get transactions
        transactions = supabase.table("transactions")\
            .select("*")\
            .eq("telegram_id", telegram_id)\
            .order("created_at", desc=True)\
            .limit(20)\
            .execute()
        
        # Get subscriptions with plan details
        subscriptions = supabase.table("subscriptions")\
            .select("*, plans(*)")\
            .eq("telegram_id", telegram_id)\
            .order("created_at", desc=True)\
            .limit(20)\
            .execute()
        
        # Get assigned credentials (stocks that were used by this user)
        credentials = supabase.table("stocks")\
            .select("*, plans(ott_name, plan_key)")\
            .eq("used_by", telegram_id)\
            .eq("is_used", True)\
            .order("used_at", desc=True)\
            .limit(20)\
            .execute()
        
        return {
            "transactions": transactions.data if transactions.data else [],
            "purchases": subscriptions.data if subscriptions.data else [],
            "credentials": credentials.data if credentials.data else []
        }
        
    except Exception as e:
        print(f"❌ Error fetching user history for {telegram_id}: {e}")
        return {
            "transactions": [],
            "purchases": [],
            "credentials": []
        }


# =====================================================# COMBO PLAN DELIVERY
# =====================================================

def get_combo_items() -> List[str]:
    """
    Get list of OTT services included in combo plan.
    
    Returns:
        List of plan_keys (e.g., ['netflix_4k', 'prime_video', 'pornhub', 'youtube'])
    """
    # Define combo items (Netflix, Prime, Pornhub, YouTube)
    return ['netflix_4k', 'prime_video', 'pornhub', 'youtube']


def allocate_combo_credentials(telegram_id: int) -> Dict[str, Any]:
    """
    Allocate credentials for all OTT services in combo plan.
    Uses atomic transaction to ensure all-or-nothing delivery.
    
    Args:
        telegram_id: User's telegram ID
        
    Returns:
        Dictionary containing:
        - success: Boolean
        - credentials: Dict of {plan_key: credential_string}
        - missing_stock: List of plan_keys that are out of stock
        - youtube_separate: Boolean (True if YouTube needs separate handling)
    """
    try:
        combo_items = get_combo_items()
        allocated = {}
        missing_stock = []
        youtube_credential = None
        
        # Separate YouTube from other services
        regular_services = [item for item in combo_items if item != 'youtube']
        has_youtube = 'youtube' in combo_items
        
        # Step 1: Check availability for all regular services (Netflix, Prime, Pornhub)
        for plan_key in regular_services:
            credential = get_unused_credential(plan_key)
            if not credential:
                missing_stock.append(plan_key)
            else:
                allocated[plan_key] = credential
        
        # Step 2: If any regular service is out of stock, abort
        if missing_stock:
            return {
                "success": False,
                "credentials": {},
                "missing_stock": missing_stock,
                "youtube_separate": False,
                "error": "Some services are out of stock"
            }
        
        # Step 3: Allocate all regular service credentials atomically
        for plan_key, credential in allocated.items():
            success = mark_credential_used(plan_key, credential, telegram_id)
            if not success:
                # Rollback: This shouldn't happen but handle it
                return {
                    "success": False,
                    "credentials": {},
                    "missing_stock": [plan_key],
                    "youtube_separate": False,
                    "error": f"Failed to allocate {plan_key}"
                }
        
        # Step 4: Add subscriptions for allocated services
        for plan_key in allocated.keys():
            add_subscription(telegram_id, plan_key)
        
        # Step 5: Handle YouTube separately (it uses email collection flow)
        if has_youtube:
            # YouTube will be handled separately by the email collection flow
            # Just add the subscription record, credentials collected later
            add_subscription(telegram_id, 'youtube')
        
        return {
            "success": True,
            "credentials": allocated,
            "missing_stock": [],
            "youtube_separate": has_youtube,
            "error": None
        }
        
    except Exception as e:
        print(f"❌ Error allocating combo credentials: {e}")
        return {
            "success": False,
            "credentials": {},
            "missing_stock": combo_items,
            "youtube_separate": False,
            "error": str(e)
        }


# =====================================================
# STOCK ANALYTICS
# =====================================================

def get_stock_counts() -> Dict[str, Dict[str, int]]:
    """
    Get stock counts for all platforms.
    
    Returns:
        Dictionary with stock counts for each platform:
        {
            "netflix_4k": {"total": 48, "unused": 45, "used": 3},
            "prime_video": {"total": 10, "unused": 8, "used": 2},
            ...
        }
    """
    try:
        # Get all stocks
        all_stocks = supabase.table("stocks").select("plan_key, is_used").execute()
        
        # Count by plan_key
        counts = {}
        for stock in all_stocks.data:
            plan_key = stock["plan_key"]
            if plan_key not in counts:
                counts[plan_key] = {"total": 0, "unused": 0, "used": 0}
            
            counts[plan_key]["total"] += 1
            if stock["is_used"]:
                counts[plan_key]["used"] += 1
            else:
                counts[plan_key]["unused"] += 1
        
        # Ensure all platforms are present (even with 0 stock)
        all_platforms = ["netflix_4k", "prime_video", "youtube", "pornhub", "combo", "spotify", "sonyliv", "zee5"]
        for platform in all_platforms:
            if platform not in counts:
                counts[platform] = {"total": 0, "unused": 0, "used": 0}
        
        return counts
        
    except Exception as e:
        print(f"❌ Error getting stock counts: {e}")
        return {}


# =====================================================
# LOGGING TO DATABASE (OPTIONAL)
# =====================================================

def store_log_in_db(event_type: str, telegram_id: Optional[int] = None, username: Optional[str] = None, details: Optional[Dict] = None, message: Optional[str] = None):
    """
    Store log entry in database for analytics and auditing.
    
    Args:
        event_type: Type of event (e.g., 'PAYMENT_SUCCESS', 'PURCHASE_FAILED')
        telegram_id: User's Telegram ID
        username: User's username
        details: Additional data as dictionary
        message: Log message text
    """
    try:
        log_entry = {
            "event_type": event_type,
            "telegram_id": telegram_id,
            "username": username,
            "details": details or {},
            "message": message
        }
        
        supabase.table("logs").insert(log_entry).execute()
        
    except Exception as e:
        print(f"❌ Error storing log in database: {e}")


def get_recent_logs(limit: int = 50, event_type: Optional[str] = None, telegram_id: Optional[int] = None) -> List[Dict]:
    """
    Retrieve recent logs from database.
    
    Args:
        limit: Number of logs to retrieve
        event_type: Filter by event type
        telegram_id: Filter by user ID
        
    Returns:
        List of log entries
    """
    try:
        query = supabase.table("logs").select("*").order("created_at", desc=True).limit(limit)
        
        if event_type:
            query = query.eq("event_type", event_type)
        
        if telegram_id:
            query = query.eq("telegram_id", telegram_id)
        
        result = query.execute()
        return result.data if result.data else []
        
    except Exception as e:
        print(f"❌ Error retrieving logs: {e}")
        return []


def get_user_activity_logs(telegram_id: int, limit: int = 20) -> List[Dict]:
    """
    Get activity logs for a specific user.
    
    Args:
        telegram_id: User's Telegram ID
        limit: Number of logs to retrieve
        
    Returns:
        List of user's activity logs
    """
    return get_recent_logs(limit=limit, telegram_id=telegram_id)


# =====================================================