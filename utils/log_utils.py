import asyncio
from datetime import datetime
from aiogram import Bot
from config.settings import BOT_TOKEN, LOG_CHANNEL_ID
from typing import Optional


def format_timestamp() -> str:
    """Returns formatted timestamp: DD/MM/YYYY HH:MM:SS"""
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")


def format_user(user_id: int, username: Optional[str] = None) -> str:
    """Formats user info consistently"""
    if username:
        return f"@{username} (ID: `{user_id}`)"
    return f"ID: `{user_id}`"


async def send_log(message: str):
    """
    Sends a formatted log message to the configured Telegram log channel.
    Automatically handles errors and safely closes the bot session.
    """
    bot = Bot(token=BOT_TOKEN)
    try:
        # Prevent sending overly long messages
        if len(message) > 4000:
            message = message[:4000] + "\n\n[⚠️ Log truncated due to length]"

        await bot.send_message(
            chat_id=LOG_CHANNEL_ID,
            text=message,
            parse_mode="Markdown"
        )

    except Exception as e:
        # More specific error handling
        if "LOGS_CHANNEL_ID" in str(e):
            print(f"[LOG ERROR] Channel ID configuration issue (using LOG_CHANNEL_ID): {e}")
        elif "parse entities" in str(e).lower():
            # Fallback: try sending without markdown if parsing fails
            try:
                await bot.send_message(
                    chat_id=LOG_CHANNEL_ID,
                    text=message.replace("*", "").replace("`", "").replace("_", ""),
                    parse_mode=None
                )
            except:
                print(f"[LOG ERROR] Failed to send log even without markdown: {e}")
        else:
            print(f"[LOG ERROR] Failed to send log message: {e}")

    finally:
        # ✅ Proper way to close the bot session in Aiogram 2.23+
        try:
            session = await bot.get_session()
            await session.close()
        except Exception:
            pass  # Ignore session close errors


# =====================================================
# USER EVENTS
# =====================================================

async def log_user_start(user_id: int, username: Optional[str] = None, is_new: bool = False):
    """Log when a user starts the bot"""
    emoji = "🆕" if is_new else "👤"
    event = "NEW USER REGISTERED" if is_new else "USER STARTED BOT"
    
    message = (
        f"{emoji} *{event}*\n\n"
        f"User: {format_user(user_id, username)}\n"
        f"Time: `{format_timestamp()}`"
    )
    await send_log(message)


async def log_user_blocked(user_id: int, username: Optional[str] = None):
    """Log when a user blocks the bot"""
    message = (
        f"🚫 *USER BLOCKED BOT*\n\n"
        f"User: {format_user(user_id, username)}\n"
        f"Time: `{format_timestamp()}`"
    )
    await send_log(message)


# =====================================================
# PAYMENT EVENTS
# =====================================================

async def log_payment_pending(user_id: int, username: Optional[str], amount: int, order_id: str):
    """Log when payment QR is generated and waiting"""
    message = (
        f"⏳ *PAYMENT PENDING*\n\n"
        f"User: {format_user(user_id, username)}\n"
        f"Amount: ₹{amount}\n"
        f"Order ID: `{order_id}`\n"
        f"Status: Waiting for payment\n"
        f"Time: `{format_timestamp()}`"
    )
    await send_log(message)


async def log_payment_success(user_id: int, username: Optional[str], amount: int, order_id: str, utr: Optional[str] = None):
    """Log successful payment"""
    utr_text = f"UTR: `{utr}`\n" if utr else ""
    message = (
        f"✅ *PAYMENT SUCCESSFUL*\n\n"
        f"User: {format_user(user_id, username)}\n"
        f"Amount: ₹{amount}\n"
        f"Order ID: `{order_id}`\n"
        f"{utr_text}"
        f"Time: `{format_timestamp()}`"
    )
    await send_log(message)


async def log_payment_failed(user_id: int, username: Optional[str], amount: int, order_id: str, reason: str):
    """Log failed payment"""
    message = (
        f"❌ *PAYMENT FAILED*\n\n"
        f"User: {format_user(user_id, username)}\n"
        f"Amount: ₹{amount}\n"
        f"Order ID: `{order_id}`\n"
        f"Reason: {reason}\n"
        f"Time: `{format_timestamp()}`"
    )
    await send_log(message)


async def log_payment_timeout(user_id: int, username: Optional[str], amount: int, order_id: str):
    """Log payment timeout/expiration"""
    message = (
        f"⏱️ *PAYMENT TIMEOUT*\n\n"
        f"User: {format_user(user_id, username)}\n"
        f"Amount: ₹{amount}\n"
        f"Order ID: `{order_id}`\n"
        f"Status: Payment expired without completion\n"
        f"Time: `{format_timestamp()}`"
    )
    await send_log(message)


# =====================================================
# PURCHASE EVENTS
# =====================================================

async def log_purchase_success(user_id: int, username: Optional[str], plan_name: str, price: int, order_id: str, new_balance: int):
    """Log successful OTT purchase"""
    message = (
        f"🛒 *OTT PURCHASE SUCCESS*\n\n"
        f"User: {format_user(user_id, username)}\n"
        f"Plan: {plan_name}\n"
        f"Price: ₹{price}\n"
        f"Order ID: `{order_id}`\n"
        f"Updated Balance: ₹{new_balance}\n"
        f"Time: `{format_timestamp()}`"
    )
    await send_log(message)


async def log_purchase_failed(user_id: int, username: Optional[str], plan_name: str, reason: str):
    """Log failed purchase"""
    message = (
        f"❌ *PURCHASE FAILED*\n\n"
        f"User: {format_user(user_id, username)}\n"
        f"Plan: {plan_name}\n"
        f"Reason: {reason}\n"
        f"Time: `{format_timestamp()}`"
    )
    await send_log(message)


async def log_stock_unavailable(user_id: int, username: Optional[str], plan_name: str):
    """Log when stock is unavailable"""
    message = (
        f"📦 *STOCK UNAVAILABLE*\n\n"
        f"User: {format_user(user_id, username)}\n"
        f"Plan: {plan_name}\n"
        f"⚠️ No credentials available\n"
        f"Time: `{format_timestamp()}`"
    )
    await send_log(message)


async def log_combo_partial_failure(user_id: int, username: Optional[str], allocated: list, missing: list):
    """Log combo plan partial failure"""
    message = (
        f"⚠️ *COMBO PLAN PARTIAL FAILURE*\n\n"
        f"User: {format_user(user_id, username)}\n"
        f"✅ Allocated: {', '.join(allocated)}\n"
        f"❌ Missing: {', '.join(missing)}\n"
        f"Status: Refunded\n"
        f"Time: `{format_timestamp()}`"
    )
    await send_log(message)


# =====================================================
# QR / PAYMENT FLOW EVENTS
# =====================================================

async def log_qr_generated(user_id: int, username: Optional[str], amount: int, order_id: str):
    """Log QR code generation"""
    message = (
        f"📱 *QR CODE GENERATED*\n\n"
        f"User: {format_user(user_id, username)}\n"
        f"Amount: ₹{amount}\n"
        f"Order ID: `{order_id}`\n"
        f"Time: `{format_timestamp()}`"
    )
    await send_log(message)


async def log_qr_reused(user_id: int, username: Optional[str], order_id: str):
    """Log when user tries to reuse old QR"""
    message = (
        f"♻️ *QR REUSE ATTEMPT*\n\n"
        f"User: {format_user(user_id, username)}\n"
        f"Order ID: `{order_id}`\n"
        f"Action: Redirected to new QR\n"
        f"Time: `{format_timestamp()}`"
    )
    await send_log(message)


# =====================================================
# ERROR EVENTS
# =====================================================

async def log_error(error_type: str, details: str, user_id: Optional[int] = None, username: Optional[str] = None):
    """Log system errors"""
    user_info = f"User: {format_user(user_id, username)}\n" if user_id else ""
    
    message = (
        f"🔴 *SYSTEM ERROR*\n\n"
        f"Type: {error_type}\n"
        f"{user_info}"
        f"Details: {details}\n"
        f"Time: `{format_timestamp()}`"
    )
    await send_log(message)


async def log_database_error(operation: str, details: str, user_id: Optional[int] = None):
    """Log database-specific errors"""
    user_info = f"User ID: `{user_id}`\n" if user_id else ""
    
    message = (
        f"💾 *DATABASE ERROR*\n\n"
        f"Operation: {operation}\n"
        f"{user_info}"
        f"Details: {details}\n"
        f"Time: `{format_timestamp()}`"
    )
    await send_log(message)


# =====================================================
# WALLET EVENTS
# =====================================================

async def log_wallet_credit(user_id: int, username: Optional[str], amount: int, new_balance: int, source: str):
    """Log wallet credit"""
    message = (
        f"💰 *WALLET CREDITED*\n\n"
        f"User: {format_user(user_id, username)}\n"
        f"Amount: ₹{amount}\n"
        f"Source: {source}\n"
        f"New Balance: ₹{new_balance}\n"
        f"Time: `{format_timestamp()}`"
    )
    await send_log(message)


async def log_wallet_debit(user_id: int, username: Optional[str], amount: int, new_balance: int, reason: str):
    """Log wallet debit"""
    message = (
        f"💸 *WALLET DEBITED*\n\n"
        f"User: {format_user(user_id, username)}\n"
        f"Amount: ₹{amount}\n"
        f"Reason: {reason}\n"
        f"New Balance: ₹{new_balance}\n"
        f"Time: `{format_timestamp()}`"
    )
    await send_log(message)


# =====================================================
# REFERRAL EVENTS
# =====================================================

async def log_referral(referrer_id: int, referrer_username: Optional[str], new_user_id: int, new_user_username: Optional[str]):
    """Log successful referral"""
    message = (
        f"🎁 *REFERRAL LINKED*\n\n"
        f"Referrer: {format_user(referrer_id, referrer_username)}\n"
        f"New User: {format_user(new_user_id, new_user_username)}\n"
        f"Time: `{format_timestamp()}`"
    )
    await send_log(message)


def send_log_sync(message: str):
    """
    Synchronous wrapper for send_log().
    Useful for calling logs from non-async contexts (e.g., Razorpay callbacks).
    """
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.ensure_future(send_log(message))
        else:
            loop.run_until_complete(send_log(message))
    except Exception as e:
        print(f"[LOG SYNC ERROR] {e}")


# ✅ Manual test (run this file directly to verify logs)
if __name__ == "__main__":
    test_message = (
        "🧾 *Test Log Message*\n\n"
        "This is a sample log entry to verify your OTTOnly bot logging system.\n"
        "✅ If you see this message in your logs channel, logging works perfectly!"
    )
    send_log_sync(test_message)
