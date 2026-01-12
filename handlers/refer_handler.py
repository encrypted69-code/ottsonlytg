import requests
import time
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import Dispatcher
from config.settings import RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET
from utils.supabase_db import update_wallet, get_user
from utils.text_utils import toSmallCaps
from utils.log_utils import log_event


def register_wallet_handlers(dp: Dispatcher):

    # 💰 Main Add Funds Menu
    @dp.callback_query_handler(lambda c: c.data == "add_funds")
    async def add_funds_menu(callback: types.CallbackQuery):
        keyboard = InlineKeyboardMarkup(row_width=3)
        keyboard.add(
            InlineKeyboardButton(toSmallCaps("₹15"), callback_data="add_15"),
            InlineKeyboardButton(toSmallCaps("₹25"), callback_data="add_25"),
            InlineKeyboardButton(toSmallCaps("₹49"), callback_data="add_49"),
            InlineKeyboardButton(toSmallCaps("₹99"), callback_data="add_99"),
            InlineKeyboardButton(toSmallCaps("⬅️ Back"), callback_data="main_menu")
        )
        await callback.message.edit_text(
            toSmallCaps("<b>💰 Select The Amount You Want To Add To Your Wallet:</b>"),
            parse_mode="HTML",
            reply_markup=keyboard
        )

    # 🎯 Create Razorpay Order
    @dp.callback_query_handler(lambda c: c.data.startswith("add_"))
    async def create_razorpay_order(callback: types.CallbackQuery):
        amount = int(callback.data.split("_")[1])
        user_id = callback.from_user.id

        order_data = {
            "amount": amount * 100,  # convert to paise
            "currency": "INR",
            "receipt": f"order_{user_id}_{int(time.time())}",
            "notes": {"user_id": str(user_id)},
        }

        response = requests.post(
            "https://api.razorpay.com/v1/orders",
            auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET),
            json=order_data
        )

        if response.status_code == 200:
            data = response.json()
            order_id = data["id"]

            payment_link = f"https://api.razorpay.com/v1/checkout/embedded?order_id={order_id}"

            kb = InlineKeyboardMarkup().add(
                InlineKeyboardButton(toSmallCaps("💳 Pay Now"), url=payment_link),
                InlineKeyboardButton(toSmallCaps("✅ I Have Paid"), callback_data=f"verify_payment_{order_id}_{amount}")
            )

            await callback.message.edit_text(
                toSmallCaps(f"<b>💰 Add ₹{amount} To Your Wallet\n\nClick Below To Pay, Then Tap I Have Paid To Confirm.</b>"),
                parse_mode="HTML",
                reply_markup=kb
            )

        else:
            await callback.message.answer(
                toSmallCaps("<b>⚠️ Error While Creating Order. Try Again Later.</b>"),
                parse_mode="HTML"
            )

    # ✅ Verify Payment + Referral Reward
    @dp.callback_query_handler(lambda c: c.data.startswith("verify_payment_"))
    async def verify_payment(callback: types.CallbackQuery):
        _, order_id, amount = callback.data.split("_")
        amount = int(amount)
        user_id = callback.from_user.id
        name = callback.from_user.full_name
        username = callback.from_user.username

        await callback.message.edit_text(toSmallCaps("<b>⏳ Verifying Your Payment...</b>"), parse_mode="HTML")

        res = requests.get(
            f"https://api.razorpay.com/v1/orders/{order_id}/payments",
            auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET)
        )

        if res.status_code != 200:
            await callback.message.answer(toSmallCaps("<b>⚠️ Unable To Verify Payment, Please Try Again Later.</b>"), parse_mode="HTML")
            return

        data = res.json()
        if "items" not in data or len(data["items"]) == 0:
            await callback.message.answer(toSmallCaps("<b>⚠️ No Payment Found Yet For This Order.</b>"), parse_mode="HTML")
            return

        payment = data["items"][0]
        status = payment["status"]

        if status == "captured":
            # ✅ Main wallet credit
            update_wallet(user_id, amount)
            user = get_user(user_id)
            new_balance = user.get("wallet", 0)

            await callback.message.answer(
                toSmallCaps(f"<b>✅ Payment Successful!\n\n"
                f"₹{amount} Credited To Your Wallet.\n"
                f"💰 New Balance: ₹{new_balance}</b>"),
                parse_mode="HTML"
            )

            # Log wallet top-up
            await log_event("WALLET_TOPUP_SUCCESS", {
                "user_id": user_id,
                "name": name,
                "username": username,
                "amount": amount,
                "order_id": order_id
            })

            # 🪙 Referral reward (10%)
            referrer_id = user.get("referred_by")
            if referrer_id:
                reward = int(amount * 0.10)
                update_wallet(referrer_id, reward)
                ref_user = get_user(referrer_id)
                ref_balance = ref_user.get("wallet", 0)
                ref_name = ref_user.get("name", "Unknown")

                # Log referred user top-up
                await log_event("REFERRAL_TOPUP", {
                    "user_id": user_id,
                    "name": name,
                    "username": username,
                    "referrer_id": referrer_id,
                    "referrer_name": ref_name,
                    "amount": amount
                })

                # Log referral credit
                await log_event("REFERRAL_CREDIT", {
                    "user_id": referrer_id,
                    "name": ref_name,
                    "username": ref_user.get("telegram_id"),  # Will show ID
                    "commission": reward,
                    "level": 1,
                    "buyer_id": user_id,
                    "buyer_name": name
                })

                # Notify referrer
                try:
                    await callback.bot.send_message(
                        referrer_id,
                        toSmallCaps(f"<b>🎁 Referral Bonus Received!\n\n"
                        f"Your Referral Just Added ₹{amount}.\n"
                        f"You Earned ₹{reward} (10%) Instantly!\n\n"
                        f"💰 New Balance: ₹{ref_balance}</b>"),
                        parse_mode="HTML"
                    )
                except Exception:
                    pass  # user may have blocked bot

        else:
            await callback.message.answer(
                toSmallCaps(f"<b>⚠️ Payment Not Completed Yet.\nStatus: {status}</b>"),
                parse_mode="HTML"
            )
