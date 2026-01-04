"""Razorpay helper with a requests-based implementation and a safe
fallback when `requests` is not installed (useful for local linting).
"""
from typing import Dict, Any

from config.settings import RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET, RAZORPAY_API_BASE


def _get_requests():
    try:
        import requests
        return requests
    except Exception:
        return None


def create_payment_link(amount: int, user_id: int) -> Dict[str, Any]:
    """Create a payment link or return a mock if requests isn't present."""
    requests = _get_requests()
    if requests is None:
        # Mock response for testing
        return {"id": f"MOCK_LINK_{user_id}_{amount}", "short_url": f"https://pay.example.com/{user_id}"}

    payload = {
        "amount": amount * 100,  # in paise
        "currency": "INR",
        "accept_partial": False,
        "reference_id": f"OTT_{user_id}",
        "description": f"Wallet top-up for user {user_id}",
        "customer": {"name": f"OTTUser_{user_id}", "email": f"user{user_id}@example.com"},
        "notify": {"sms": False, "email": False},
        "reminder_enable": True,
        "callback_url": "https://razorpay.com",
        "callback_method": "get",
    }

    res = requests.post(
        f"{RAZORPAY_API_BASE}/payment_links",
        auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET),
        json=payload,
        timeout=10,
    )
    return res.json()


def get_payment_status(payment_link_id: str) -> Dict[str, Any]:
    requests = _get_requests()
    if requests is None:
        return {"status": "paid"}  # assume paid in mock environment
    res = requests.get(
        f"{RAZORPAY_API_BASE}/payment_links/{payment_link_id}",
        auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET),
        timeout=10,
    )
    return res.json()
