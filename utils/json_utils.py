import json
import os
from datetime import datetime, timedelta
from config.settings import DATA_FILE, PLANS

DATA_TRANSACTIONS = "data/transactions.json"
os.makedirs(os.path.dirname(DATA_TRANSACTIONS), exist_ok=True)


# --- Helper functions for reading/writing JSON files ---

def _read_all():
    """Read user data JSON file."""
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({}, f, indent=2)
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def _write_all(data):
    """Write user data JSON file."""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def _read_transactions():
    """Read transactions JSON file."""
    if not os.path.exists(DATA_TRANSACTIONS):
        with open(DATA_TRANSACTIONS, "w") as f:
            json.dump({}, f, indent=2)
    with open(DATA_TRANSACTIONS, "r") as f:
        return json.load(f)


def _write_transactions(data):
    """Write transactions JSON file."""
    with open(DATA_TRANSACTIONS, "w") as f:
        json.dump(data, f, indent=2)


# --- User management ---

def create_user_if_not_exists(user_id: int, name: str = "", referred_by: int = None):
    """Create new user if not exists."""
    data = _read_all()
    uid = str(user_id)
    if uid not in data:
        data[uid] = {
            "id": user_id,
            "name": name,
            "wallet": 0,
            "subscriptions": [],
            "joined_at": datetime.utcnow().isoformat(),
            "referred_by": referred_by,
            "referrals": []
        }
        _write_all(data)
    return data[uid]


def get_user(user_id: int):
    """Fetch user data."""
    data = _read_all()
    return data.get(str(user_id))


def save_user_data(user_id: int, user_data: dict):
    """Save/update user data."""
    data = _read_all()
    uid = str(user_id)
    data[uid] = user_data
    _write_all(data)


def get_wallet_balance(user_id: int) -> int:
    """Return wallet balance."""
    data = _read_all()
    uid = str(user_id)
    return data.get(uid, {}).get("wallet", 0)


def set_referred_by(user_id: int, referrer_id: int):
    """Set parent referral relationship."""
    data = _read_all()
    uid = str(user_id)
    rid = str(referrer_id)
    if uid not in data:
        create_user_if_not_exists(user_id)
        data = _read_all()
    if data[uid].get("referred_by"):
        return False  # already referred
    data[uid]["referred_by"] = referrer_id
    if rid in data:
        data[rid].setdefault("referrals", []).append(user_id)
    _write_all(data)
    return True


# --- Wallet System ---

def update_wallet(user_id: int, amount: int):
    """Add money to wallet."""
    data = _read_all()
    uid = str(user_id)
    if uid not in data:
        create_user_if_not_exists(user_id)
        data = _read_all()
    data[uid]["wallet"] = data[uid].get("wallet", 0) + amount
    _write_all(data)
    record_transaction(user_id, "Wallet Credit", amount)
    return data[uid]["wallet"]


def deduct_wallet(user_id: int, amount: int) -> bool:
    """Deduct money from wallet."""
    data = _read_all()
    uid = str(user_id)
    if uid not in data:
        return False
    if data[uid].get("wallet", 0) < amount:
        return False
    data[uid]["wallet"] -= amount
    _write_all(data)
    record_transaction(user_id, "Wallet Debit", -amount)
    return True


def record_transaction(user_id: int, description: str, amount: int):
    """Record transaction log."""
    data = _read_transactions()
    uid = str(user_id)
    data.setdefault(uid, [])
    data[uid].append({
        "description": description,
        "amount": amount,
        "timestamp": datetime.utcnow().isoformat()
    })
    _write_transactions(data)


# --- Subscription Management ---

def add_subscription(user_id: int, plan_key: str):
    """Add OTT subscription to user's profile."""
    data = _read_all()
    uid = str(user_id)
    if plan_key not in PLANS:
        raise ValueError("Unknown plan key.")
    plan = PLANS[plan_key]
    now = datetime.utcnow()
    expiry = now + timedelta(days=30)
    sub = {
        "plan_key": plan_key,
        "name": plan["name"],
        "price": plan["price"],
        "bought_at": now.isoformat(),
        "expires_at": expiry.isoformat()
    }
    if uid not in data:
        create_user_if_not_exists(user_id)
        data = _read_all()
    data[uid].setdefault("subscriptions", []).append(sub)
    _write_all(data)
    record_transaction(user_id, f"Purchased {plan['name']}", -plan["price"])
    return sub


# --- Referral System (10% bonus) ---

def credit_referral_bonus(user_id: int, added_amount: int):
    """
    If user was referred by someone, give 10% to parent.
    """
    data = _read_all()
    uid = str(user_id)
    if uid not in data:
        return 0
    referrer_id = data[uid].get("referred_by")
    if not referrer_id:
        return 0

    parent_uid = str(referrer_id)
    bonus = int(added_amount * 0.10)
    data[parent_uid]["wallet"] = data[parent_uid].get("wallet", 0) + bonus
    _write_all(data)

    # Record both logs
    record_transaction(parent_uid, f"Referral Bonus (from {user_id})", bonus)
    record_transaction(user_id, f"Referred by {parent_uid}", 0)

    return bonus


# --- Utility: Get full transaction history ---

def get_transactions(user_id: int):
    """Return list of transactions for user."""
    data = _read_transactions()
    return data.get(str(user_id), [])
