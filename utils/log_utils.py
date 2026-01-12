"""
CENTRALIZED LOGGING SYSTEM
===========================
Clean, professional logging with 3 separate channels:
- BUSINESS_LOGS: Wallet top-ups & purchases
- ERROR_LOGS: Failed purchases & system errors
- REFERRAL_LOGS: Referral activity & commissions
"""

import asyncio
from datetime import datetime
from aiogram import Bot
from config.settings import (
    BOT_TOKEN,
    BUSINESS_LOGS_CHANNEL,
    ERROR_LOGS_CHANNEL,
    REFERRAL_LOGS_CHANNEL
)
from typing import Optional, Dict, Any

# Track logged users to prevent duplicate USER_JOIN logs
_logged_users = set()


def _format_time() -> str:
    """Returns formatted timestamp"""
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")


def _format_user(user_id: int, name: str = None, username: str = None) -> str:
    """
    Format user identity consistently.
    Always includes: User ID, Name, Username (or N/A)
    """
    username_display = f"@{username}" if username else "N/A"
    name_display = name if name else "Unknown"
    return f"👤 User ID: `{user_id}`\n👤 Name: {name_display}\n👤 Username: {username_display}"


async def _send_to_channel(channel_id: int, message: str):
    """Internal function to send message to specific channel"""
    bot = Bot(token=BOT_TOKEN)
    try:
        if len(message) > 4000:
            message = message[:4000] + "\n\n⚠️ [Truncated]"
        
        await bot.send_message(
            chat_id=channel_id,
            text=message,
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"[LOG ERROR] Failed to send to channel {channel_id}: {e}")
    finally:
        try:
            session = await bot.get_session()
            await session.close()
        except:
            pass


# =====================================================
# CENTRALIZED LOG EVENT FUNCTION
# =====================================================

async def log_event(event_type: str, payload: Dict[str, Any]):
    """
    Centralized logging function.
    
    Event Types:
    - USER_JOIN: First time user registration
    - WALLET_TOPUP_SUCCESS: Successful wallet top-up
    - PURCHASE_SUCCESS: Successful OTT purchase
    - PURCHASE_FAILED: Failed purchase
    - PAYMENT_ERROR: Payment gateway error
    - REFERRAL_JOIN: User joined via referral
    - REFERRAL_TOPUP: Referred user topped up wallet
    - REFERRAL_CREDIT: Commission credited to referrer
    - SYSTEM_ERROR: Critical system error
    """
    
    user_id = payload.get("user_id")
    name = payload.get("name", "Unknown")
    username = payload.get("username")
    
    # ==================== BUSINESS LOGS ====================
    
    if event_type == "WALLET_TOPUP_SUCCESS":
        amount = payload.get("amount", 0)
        order_id = payload.get("order_id", "N/A")
        
        message = (
            f"💰 *WALLET TOP-UP SUCCESS*\n\n"
            f"{_format_user(user_id, name, username)}\n"
            f"💵 Amount: ₹{amount}\n"
            f"🆔 Order ID: `{order_id}`\n"
            f"🕒 Time: `{_format_time()}`"
        )
        await _send_to_channel(BUSINESS_LOGS_CHANNEL, message)
    
    elif event_type == "PURCHASE_SUCCESS":
        plan_name = payload.get("plan_name", "Unknown Plan")
        price = payload.get("price", 0)
        
        message = (
            f"🎬 *PURCHASE SUCCESS*\n\n"
            f"{_format_user(user_id, name, username)}\n"
            f"📦 Plan: {plan_name}\n"
            f"💵 Price: ₹{price}\n"
            f"🕒 Time: `{_format_time()}`"
        )
        await _send_to_channel(BUSINESS_LOGS_CHANNEL, message)
    
    # ==================== ERROR LOGS ====================
    
    elif event_type == "PURCHASE_FAILED":
        reason = payload.get("reason", "Unknown")
        plan_name = payload.get("plan_name", "Unknown Plan")
        
        message = (
            f"❌ *PURCHASE FAILED*\n\n"
            f"{_format_user(user_id, name, username)}\n"
            f"📦 Plan: {plan_name}\n"
            f"⚠️ Reason: {reason}\n"
            f"🕒 Time: `{_format_time()}`"
        )
        await _send_to_channel(ERROR_LOGS_CHANNEL, message)
    
    elif event_type == "PAYMENT_ERROR":
        error = payload.get("error", "Unknown Error")
        order_id = payload.get("order_id", "N/A")
        
        message = (
            f"💳 *PAYMENT ERROR*\n\n"
            f"{_format_user(user_id, name, username)}\n"
            f"🆔 Order ID: `{order_id}`\n"
            f"⚠️ Error: {error}\n"
            f"🕒 Time: `{_format_time()}`"
        )
        await _send_to_channel(ERROR_LOGS_CHANNEL, message)
    
    elif event_type == "SYSTEM_ERROR":
        error = payload.get("error", "Unknown Error")
        context = payload.get("context", "N/A")
        
        message = (
            f"🚨 *SYSTEM ERROR*\n\n"
            f"⚠️ Error: {error}\n"
            f"📍 Context: {context}\n"
            f"🕒 Time: `{_format_time()}`"
        )
        await _send_to_channel(ERROR_LOGS_CHANNEL, message)
    
    # ==================== REFERRAL LOGS ====================
    
    elif event_type == "REFERRAL_JOIN":
        referrer_id = payload.get("referrer_id")
        referrer_name = payload.get("referrer_name", "Unknown")
        
        # Prevent duplicate logs
        if user_id in _logged_users:
            return
        _logged_users.add(user_id)
        
        message = (
            f"👥 *NEW REFERRAL JOIN*\n\n"
            f"🆕 New User:\n"
            f"{_format_user(user_id, name, username)}\n\n"
            f"👤 Referred By:\n"
            f"User ID: `{referrer_id}`\n"
            f"Name: {referrer_name}\n"
            f"🕒 Time: `{_format_time()}`"
        )
        await _send_to_channel(REFERRAL_LOGS_CHANNEL, message)
    
    elif event_type == "REFERRAL_TOPUP":
        referrer_id = payload.get("referrer_id")
        referrer_name = payload.get("referrer_name", "Unknown")
        amount = payload.get("amount", 0)
        
        message = (
            f"💰 *REFERRED USER TOP-UP*\n\n"
            f"💵 Referred User Topped Up: ₹{amount}\n\n"
            f"👤 Referred User:\n"
            f"{_format_user(user_id, name, username)}\n\n"
            f"👤 Referrer:\n"
            f"User ID: `{referrer_id}`\n"
            f"Name: {referrer_name}\n"
            f"🕒 Time: `{_format_time()}`"
        )
        await _send_to_channel(REFERRAL_LOGS_CHANNEL, message)
    
    elif event_type == "REFERRAL_CREDIT":
        commission = payload.get("commission", 0)
        level = payload.get("level", 1)
        buyer_id = payload.get("buyer_id")
        buyer_name = payload.get("buyer_name", "Unknown")
        
        level_text = "Direct (Level 1)" if level == 1 else "Indirect (Level 2)"
        
        message = (
            f"💸 *REFERRAL COMMISSION CREDITED*\n\n"
            f"👤 Referrer:\n"
            f"{_format_user(user_id, name, username)}\n\n"
            f"💰 Commission: ₹{commission}\n"
            f"📊 Level: {level_text}\n\n"
            f"👤 Purchase By:\n"
            f"User ID: `{buyer_id}`\n"
            f"Name: {buyer_name}\n"
            f"🕒 Time: `{_format_time()}`"
        )
        await _send_to_channel(REFERRAL_LOGS_CHANNEL, message)


# =====================================================
# LEGACY COMPATIBILITY (Optional - for gradual migration)
# =====================================================

async def send_log(message: str):
    """
    Legacy function - sends to business logs channel.
    USE log_event() INSTEAD for new code.
    """
    await _send_to_channel(BUSINESS_LOGS_CHANNEL, message)
