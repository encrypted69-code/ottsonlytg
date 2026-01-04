"""
Database utilities for managing OTT plans and credentials stock
"""
import json
import os
from datetime import datetime
from typing import Optional, List, Dict

PLANS_DB = "data/plans.json"
STOCKS_DB = "data/stocks.json"

os.makedirs("data", exist_ok=True)


# ========== PLANS DATABASE ==========

def _read_plans():
    """Read plans database"""
    if not os.path.exists(PLANS_DB):
        with open(PLANS_DB, "w") as f:
            json.dump({}, f, indent=2)
    with open(PLANS_DB, "r") as f:
        return json.load(f)


def _write_plans(data):
    """Write plans database"""
    with open(PLANS_DB, "w") as f:
        json.dump(data, f, indent=2)


def _read_stocks():
    """Read stocks database"""
    if not os.path.exists(STOCKS_DB):
        with open(STOCKS_DB, "w") as f:
            json.dump({}, f, indent=2)
    with open(STOCKS_DB, "r") as f:
        return json.load(f)


def _write_stocks(data):
    """Write stocks database"""
    with open(STOCKS_DB, "w") as f:
        json.dump(data, f, indent=2)


# ========== PLAN MANAGEMENT ==========

def get_plan(plan_key: str) -> Optional[Dict]:
    """Get plan details"""
    plans = _read_plans()
    return plans.get(plan_key)


def get_all_plans() -> Dict:
    """Get all plans"""
    return _read_plans()


def create_plan(plan_key: str, ott_name: str, price: int, description: str = ""):
    """Create new plan"""
    plans = _read_plans()
    plans[plan_key] = {
        "plan_key": plan_key,
        "ott_name": ott_name,
        "price": price,
        "description": description,
        "stock": 0,
        "active": True,
        "created_at": datetime.now().isoformat()
    }
    _write_plans(plans)


def update_plan_price(plan_key: str, price: int):
    """Update plan price"""
    plans = _read_plans()
    if plan_key in plans:
        plans[plan_key]["price"] = price
        _write_plans(plans)


def update_plan_details(plan_key: str, description: str):
    """Update plan description"""
    plans = _read_plans()
    if plan_key in plans:
        plans[plan_key]["description"] = description
        _write_plans(plans)


def toggle_plan_active(plan_key: str):
    """Toggle plan active status"""
    plans = _read_plans()
    if plan_key in plans:
        plans[plan_key]["active"] = not plans[plan_key].get("active", True)
        _write_plans(plans)
        return plans[plan_key]["active"]
    return None


def get_plan_stock_count(plan_key: str) -> int:
    """Get available stock count for plan"""
    stocks = _read_stocks()
    plan_stocks = stocks.get(plan_key, [])
    return len([s for s in plan_stocks if not s.get("used", False)])


def update_plan_stock_count(plan_key: str):
    """Update stock count in plan"""
    plans = _read_plans()
    if plan_key in plans:
        plans[plan_key]["stock"] = get_plan_stock_count(plan_key)
        _write_plans(plans)


# ========== STOCK MANAGEMENT ==========

def add_credentials(plan_key: str, credentials_list: List[str]) -> Dict:
    """
    Add credentials to stock
    Returns: {"added": count, "duplicates": count, "total": count}
    """
    stocks = _read_stocks()
    
    if plan_key not in stocks:
        stocks[plan_key] = []
    
    existing_creds = [s["credentials"] for s in stocks[plan_key]]
    added = 0
    duplicates = 0
    
    for cred in credentials_list:
        cred = cred.strip()
        if not cred:
            continue
            
        if cred in existing_creds:
            duplicates += 1
            continue
        
        stocks[plan_key].append({
            "credentials": cred,
            "used": False,
            "added_at": datetime.now().isoformat(),
            "used_at": None,
            "used_by": None
        })
        added += 1
    
    _write_stocks(stocks)
    update_plan_stock_count(plan_key)
    
    return {
        "added": added,
        "duplicates": duplicates,
        "total": len(stocks[plan_key])
    }


def get_unused_credential(plan_key: str) -> Optional[str]:
    """Get one unused credential"""
    stocks = _read_stocks()
    plan_stocks = stocks.get(plan_key, [])
    
    for stock in plan_stocks:
        if not stock.get("used", False):
            return stock["credentials"]
    
    return None


def mark_credential_used(plan_key: str, credentials: str, user_id: int):
    """Mark credential as used"""
    stocks = _read_stocks()
    plan_stocks = stocks.get(plan_key, [])
    
    for stock in plan_stocks:
        if stock["credentials"] == credentials and not stock.get("used", False):
            stock["used"] = True
            stock["used_at"] = datetime.now().isoformat()
            stock["used_by"] = user_id
            _write_stocks(stocks)
            update_plan_stock_count(plan_key)
            return True
    
    return False


def get_all_stock_for_plan(plan_key: str) -> List[Dict]:
    """Get all stock for a plan"""
    stocks = _read_stocks()
    return stocks.get(plan_key, [])


# ========== INITIALIZATION ==========

def initialize_default_plans():
    """Initialize default plans if not exist"""
    plans = _read_plans()
    
    default_plans = {
        "netflix_4k": {
            "plan_key": "netflix_4k",
            "ott_name": "Netflix 4K",
            "price": 99,
            "description": "Private Single Screen | Supports TV/Laptop/Mobile | 1 Month",
            "stock": 0,
            "active": True,
            "created_at": datetime.now().isoformat()
        },
        "prime_video": {
            "plan_key": "prime_video",
            "ott_name": "Prime Video",
            "price": 45,
            "description": "Private Single Screen | Full HD Quality | 1 Month",
            "stock": 0,
            "active": True,
            "created_at": datetime.now().isoformat()
        },
        "youtube": {
            "plan_key": "youtube",
            "ott_name": "YouTube Premium",
            "price": 15,
            "description": "Delivered to Gmail | Ad-Free YouTube + Music | 1 Month",
            "stock": 0,
            "active": True,
            "created_at": datetime.now().isoformat()
        },
        "spotify": {
            "plan_key": "spotify",
            "ott_name": "Spotify Premium",
            "price": 29,
            "description": "Private Account | Ad-Free Music | 1 Month",
            "stock": 0,
            "active": True,
            "created_at": datetime.now().isoformat()
        },
        "sonyliv": {
            "plan_key": "sonyliv",
            "ott_name": "Sony Liv",
            "price": 39,
            "description": "Private Account | Sports + Movies | 1 Month",
            "stock": 0,
            "active": True,
            "created_at": datetime.now().isoformat()
        },
        "zee5": {
            "plan_key": "zee5",
            "ott_name": "Zee5 Premium",
            "price": 35,
            "description": "Private Account | Movies + TV Shows | 1 Month",
            "stock": 0,
            "active": True,
            "created_at": datetime.now().isoformat()
        },
        "combo": {
            "plan_key": "combo",
            "ott_name": "Combo Pack",
            "price": 99,
            "description": "Multiple OTT Platforms | Best Value | 1 Month",
            "stock": 0,
            "active": True,
            "created_at": datetime.now().isoformat()
        },
        "pornhub": {
            "plan_key": "pornhub",
            "ott_name": "Pornhub Premium",
            "price": 49,
            "description": "Private Account | HD Content | 1 Month",
            "stock": 0,
            "active": True,
            "created_at": datetime.now().isoformat()
        }
    }
    
    # Only add plans that don't exist
    for key, plan in default_plans.items():
        if key not in plans:
            plans[key] = plan
    
    _write_plans(plans)


# Initialize on import
initialize_default_plans()
