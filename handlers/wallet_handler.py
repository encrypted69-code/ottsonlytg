import asyncio
import time
import random
import string
import qrcode
import requests
from io import BytesIO
from datetime import datetime
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputFile
from config.settings import (
    UPI_ID,
    MERCHANT_ID,
    PAY_VERIFY_API,
    LOG_CHANNEL_ID,
)
from utils.supabase_db import update_wallet, get_user, get_wallet_balance, create_user_if_not_exists
from utils.log_utils import send_log
from utils.text_utils import toSmallCaps


def register_wallet(dp):
    """
    Handles wallet top-up using UPI QR code payment gateway with Paytm Merchant.
    """

    # Track users waiting to enter custom amount
    waiting_for_custom_amount = {}

    # ========== HELPER FUNCTIONS ==========
    
    def generate_order_id(user_id):
        """Generate unique order ID for payment tracking"""
        ts = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"M-{user_id}-{ts}"

    def generate_qr(plan_name, amount, order_id):
        """Generate UPI QR code for payment"""
        upi = (
            f"upi://pay?pa={UPI_ID}"
            f"&pn={plan_name}"
            f"&tr={order_id}"
            f"&tn={order_id}"
            f"&am={amount}"
            f"&cu=INR"
        )
        img = qrcode.make(upi)
        bio = BytesIO()
        bio.name = "payment_qr.png"
        img.save(bio, "PNG")
        bio.seek(0)
        return bio, upi

    def verify_payment(order_id):
        """Verify payment status from Paytm merchant"""
        try:
            url = f"{PAY_VERIFY_API}?mid={MERCHANT_ID}&oid={order_id}"
            print(f"[VERIFY_PAYMENT] Calling URL: {url}")
            r = requests.get(url, timeout=15)
            print(f"[VERIFY_PAYMENT] Response Status: {r.status_code}")
            print(f"[VERIFY_PAYMENT] Response Text: {r.text}")
            
            if r.status_code != 200:
                print(f"[VERIFY_PAYMENT] Non-200 status code, returning None")
                return None
            
            data = r.json()
            print(f"[VERIFY_PAYMENT] JSON Data: {data}")
            
            if data.get("STATUS") == "TXN_SUCCESS":
                print(f"[VERIFY_PAYMENT] Payment SUCCESS found!")
                return data
            
            print(f"[VERIFY_PAYMENT] Payment status is not TXN_SUCCESS, it's: {data.get('STATUS')}")
            return None
        except Exception as e:
            print(f"[VERIFY_PAYMENT] Exception: {e}")
            return None

    # ========== MENU: Add Funds ==========
    @dp.callback_query_handler(lambda c: c.data == "menu_add_funds")
    async def menu_add_funds(callback_query: types.CallbackQuery):
        kb = InlineKeyboardMarkup(row_width=1)
        kb.add(
            InlineKeyboardButton(toSmallCaps("✏️ Enter Custom Amount"), callback_data="addfunds_custom")
        )
        kb.add(InlineKeyboardButton(toSmallCaps("⬅️ Back"), callback_data="back_to_main"))
        await callback_query.message.edit_text(
            toSmallCaps("<b>💰 Add Funds To Your Wallet\n\nClick Below To Enter Any Amount You Want:</b>"),
            parse_mode="HTML",
            reply_markup=kb,
        )
        await callback_query.answer()

    # ========== ASK FOR CUSTOM AMOUNT ==========
    @dp.callback_query_handler(lambda c: c.data == "addfunds_custom")
    async def ask_custom_amount(callback_query: types.CallbackQuery):
        user_id = callback_query.from_user.id
        waiting_for_custom_amount[user_id] = True
        
        # Delete previous messages for cleaner interface
        try:
            await callback_query.message.delete()
        except:
            pass
        
        await callback_query.bot.send_message(
            chat_id=user_id,
            text=toSmallCaps("<b>💰 Enter Custom Amount\n\nPlease Enter The Amount You Want To Add (₹):\n\nExample: 1 or 50 or 100 or 500\n\nMaximum: ₹10,000</b>"),
            parse_mode="HTML"
        )
        await callback_query.answer()

    # ========== HANDLE CUSTOM AMOUNT INPUT ==========
    @dp.message_handler(lambda message: message.text and message.text.isdigit())
    async def handle_custom_amount_input(message: types.Message):
        user_id = message.from_user.id
        
        # Check if user is waiting to enter custom amount
        if user_id not in waiting_for_custom_amount:
            return  # Not waiting for custom amount
        
        # Clear the flag
        del waiting_for_custom_amount[user_id]
        
        amount = int(message.text)
        
        # Validate amount (no minimum, maximum ₹10000)
        if amount < 1:
            await message.answer(
                toSmallCaps("<b>⚠️ Invalid Amount!\n\nPlease Enter At Least ₹1.</b>"),
                parse_mode="HTML"
            )
            return
        
        if amount > 10000:
            await message.answer(
                toSmallCaps("<b>⚠️ Amount Too High!\n\nMaximum Amount Is ₹10,000. Please Try Again.</b>"),
                parse_mode="HTML"
            )
            return
        
        # Delete user's message
        try:
            await message.delete()
        except:
            pass
        
        username = message.from_user.username or "NoUsername"
        
        try:
            # Generate unique order ID
            order_id = generate_order_id(user_id)
            
            # Generate QR code
            qr_buffer, upi_string = generate_qr("OTTOnly Wallet", amount, order_id)
            
            # Send QR code image
            text = toSmallCaps(
                f"<b>💳 Payment QR Code Generated!\n\n"
                f"💰 Amount: ₹{amount}\n"
                f"🆔 Order ID: {order_id}\n\n"
                f"📱 Scan QR Code To Pay\n"
                f"Or Click 'Check Status' After Payment.</b>"
            )

            kb = InlineKeyboardMarkup().add(
                InlineKeyboardButton(toSmallCaps("✅ Check Payment Status"), callback_data=f"checkpay_{order_id}_{amount}")
            )
            
            # Send QR code as photo
            await message.answer_photo(
                photo=InputFile(qr_buffer),
                caption=text,
                parse_mode="HTML",
                reply_markup=kb
            )
            
            await send_log(f"💳 *Payment QR Created (Custom)*\n👤 User: `{user_id}` (@{username})\n💰 Amount: ₹{amount}\n🆔 Order ID: `{order_id}`")

        except Exception as e:
            error_msg = toSmallCaps(f"<b>❌ Payment QR Generation Failed.\n\n📝 Error Details:\n{str(e)}</b>")
            await message.answer(error_msg, parse_mode="HTML")
            await send_log(f"❌ *Payment QR Failed (Custom)*\n👤 User: `{user_id}` (@{username})\n💰 Amount: ₹{amount}\n🚨 Error: {str(e)}")

    # ========== CREATE PAYMENT & SEND QR CODE ==========
    @dp.callback_query_handler(lambda c: c.data.startswith("addfunds_") and c.data != "addfunds_custom")
    async def process_addfunds(callback_query: types.CallbackQuery):
        amount = int(callback_query.data.split("_")[1])
        user_id = callback_query.from_user.id
        username = callback_query.from_user.username or "NoUsername"

        try:
            # Generate unique order ID
            order_id = generate_order_id(user_id)
            
            # Generate QR code
            qr_buffer, upi_string = generate_qr("OTTOnly Wallet", amount, order_id)
            
            # Send QR code image
            text = toSmallCaps(
                f"<b>ðŸ’³ Payment QR Code Generated!\n\n"
                f"ðŸ’° Amount: â‚¹{amount}\n"
                f"ðŸ†” Order ID: {order_id}\n\n"
                f"ðŸ“± Scan QR Code To Pay\n"
                f"Or Click 'Check Status' After Payment.</b>"
            )

            kb = InlineKeyboardMarkup().add(
                InlineKeyboardButton(toSmallCaps("âœ… Check Payment Status"), callback_data=f"checkpay_{order_id}_{amount}")
            )
            
            # Send QR code as photo
            await callback_query.message.answer_photo(
                photo=InputFile(qr_buffer),
                caption=text,
                parse_mode="HTML",
                reply_markup=kb
            )
            
            await callback_query.answer()
            await send_log(f"ðŸ’³ *Payment QR Created*\nðŸ‘¤ User: `{user_id}` (@{username})\nðŸ’° Amount: â‚¹{amount}\nðŸ†” Order ID: `{order_id}`")

        except Exception as e:
            error_msg = toSmallCaps(f"<b>âŒ Payment QR Generation Failed.\n\nðŸ” Error Details:\n{str(e)}</b>")
            kb = InlineKeyboardMarkup().add(
                InlineKeyboardButton(toSmallCaps("ðŸ”„ Retry"), callback_data=f"addfunds_{amount}"),
                InlineKeyboardButton(toSmallCaps("â¬…ï¸ Back"), callback_data="back_to_main")
            )
            await callback_query.message.edit_text(error_msg, parse_mode="HTML", reply_markup=kb)
            await send_log(f"âŒ *Payment QR Failed*\nðŸ‘¤ User: `{user_id}` (@{username})\nðŸ’° Amount: â‚¹{amount}\nðŸš¨ Error: {str(e)}")

    # ========== CHECK PAYMENT STATUS ==========
    @dp.callback_query_handler(lambda c: c.data.startswith("checkpay_"))
    async def check_payment_status(callback_query: types.CallbackQuery):
        print(f"[PAYMENT CHECK] Handler triggered! Callback data: {callback_query.data}")
        
        # Parse callback data: checkpay_ORDER_ID_AMOUNT
        parts = callback_query.data.split("_")
        if len(parts) < 3:
            await callback_query.answer("âŒ Invalid payment data", show_alert=True)
            return
            
        order_id = "_".join(parts[1:-1])  # Handle order_id with underscores
        amount = int(parts[-1])
        user_id = callback_query.from_user.id
        username = callback_query.from_user.username or "NoUsername"
        
        print(f"[PAYMENT CHECK] Parsed - Order ID: {order_id}, Amount: {amount}, User: {user_id}")

        await callback_query.answer("⏳ Checking payment status...")

        try:
            # Verify payment
            print(f"[PAYMENT CHECK] Calling verify_payment for order {order_id}...")
            payment_data = verify_payment(order_id)
            print(f"[PAYMENT CHECK] Payment data received: {payment_data}")
            
            if payment_data:
                # Check if already processed
                user_data = get_user(user_id)
                if not user_data:
                    user_data = create_user_if_not_exists(user_id, username)
                
                processed_payments = user_data.get("processed_payments", [])
                
                if order_id in processed_payments:
                    await callback_query.message.edit_caption(
                        caption=toSmallCaps("<b>âœ… This Payment Was Already Processed!</b>"),
                        parse_mode="HTML"
                    )
                    return
                
                # Process payment
                print(f"[PAYMENT CHECK] Processing payment - crediting {amount} to user {user_id}")
                update_wallet(user_id, amount, "add")
                print(f"[PAYMENT CHECK] Wallet updated!")
                
                # Get new balance using the dedicated function
                new_balance = get_wallet_balance(user_id)
                print(f"[PAYMENT CHECK] New balance: {new_balance}")
                
                # Mark as processed
                from utils.supabase_db import mark_payment_processed
                mark_payment_processed(user_id, order_id)
                
                # Show success popup
                await callback_query.answer(
                    f"✅ Payment Success! ₹{amount} added to your wallet!",
                    show_alert=True
                )
                
                # Delete the QR code message
                try:
                    await callback_query.message.delete()
                except:
                    pass
                
                # Send new success message
                await callback_query.bot.send_message(
                    chat_id=user_id,
                    text=toSmallCaps(
                        f"<b>✅ Payment Successful!\n\n"
                        f"Your Wallet Was Funded With ₹{amount}\n\n"
                        f"💰 Your New Balance = ₹{new_balance}\n\n"
                        f"Thank You! 🙏</b>"
                    ),
                    parse_mode="HTML"
                )

                # Handle referral bonus (10%)
                if user_data and user_data.get("referred_by"):
                    referrer_id = user_data["referred_by"]
                    bonus = int(amount * 0.10)
                    referrer_balance = update_wallet(referrer_id, bonus)
                    await send_log(
                        f"ðŸŽ *Referral Bonus Added!*\n"
                        f"ðŸ‘¤ Referrer: `{referrer_id}`\n"
                        f"ðŸ‘¶ Child: `{user_id}` (@{username})\n"
                        f"ðŸ’° Bonus: â‚¹{bonus}\n"
                        f"ðŸ¦ New Balance: â‚¹{referrer_balance}"
                    )

                await send_log(
                    f"âœ… *Payment Verified & Credited*\n"
                    f"ðŸ‘¤ User: `{user_id}` (@{username})\n"
                    f"ðŸ’° Amount: â‚¹{amount}\n"
                    f"ðŸ†” Order ID: `{order_id}`\n"
                    f"ðŸ¦ New Balance: â‚¹{new_balance}"
                )
                
            else:
                # Payment not found - show alert and keep button active
                await callback_query.answer("⏳ Payment not confirmed yet. Please wait and try again.", show_alert=True)
                print(f"[PAYMENT CHECK] Payment not found for order {order_id}")
                
        except Exception as e:
            error_msg = f"❌ Error checking payment: {str(e)}"
            print(f"[PAYMENT CHECK ERROR] {error_msg}")
            await callback_query.answer(error_msg, show_alert=True)
            await send_log(f"❌ *Payment Check Error*\n👤 User: `{user_id}`\n🆔 Order ID: `{order_id}`\n🚨 Error: {str(e)}")

