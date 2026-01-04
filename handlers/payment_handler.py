# handlers/wallet_handler.py
import asyncio
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.supabase_db import get_wallet_balance, update_wallet
from utils.razorpay_api import create_payment_link, get_payment_status
from config.settings import PAYMENT_CHECK_INTERVAL

pending_payments = {}  # {user_id: {"link_id": "", "amount": int}}

def register_wallet(dp):
    @dp.callback_query_handler(lambda c: c.data == 'wallet_menu')
    async def wallet_menu_handler(callback_query: types.CallbackQuery):
        uid = callback_query.from_user.id
        bal = get_wallet_balance(uid)
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("🟢 Add Funds", callback_data="add_funds"))
        kb.add(InlineKeyboardButton("⬅️ Back", callback_data="back_to_main"))
        await callback_query.message.edit_text(f"💰 Wallet balance: ₹{bal}", reply_markup=kb)
        await callback_query.answer()

    @dp.callback_query_handler(lambda c: c.data == 'add_funds')
    async def add_funds_start(callback_query: types.CallbackQuery):
        await callback_query.message.answer("Enter amount to add (in ₹). Example: 100")
        await callback_query.answer()

    @dp.message_handler(lambda m: m.text and m.text.isdigit())
    async def receive_amount(message: types.Message):
        amount = int(message.text.strip())
        uid = message.from_user.id
        payment_data = create_payment_link(amount, uid)

        if not payment_data.get("id"):
            await message.reply("❌ Failed to create payment link. Try again later.")
            return

        link_id = payment_data["id"]
        short_url = payment_data.get("short_url", "")
        pending_payments[uid] = {"link_id": link_id, "amount": amount}

        await message.reply(
            f"💳 Click below to pay securely:\n[Pay Now]({short_url})\n\nOnce you complete payment, your wallet will update automatically.",
            parse_mode="Markdown"
        )

        # Start background polling
        asyncio.create_task(check_payment_status_loop(uid, link_id, amount, message))

async def check_payment_status_loop(uid, link_id, amount, message):
    """Background loop to check Razorpay payment status."""
    for _ in range(20):  # check for 5 mins (20 x 15s)
        await asyncio.sleep(PAYMENT_CHECK_INTERVAL)
        status_data = get_payment_status(link_id)
        if status_data.get("status") == "paid":
            update_wallet(uid, amount)
            await message.answer(f"✅ Payment received! ₹{amount} added to your wallet.")
            pending_payments.pop(uid, None)
            return
    await message.answer("⚠️ Payment not completed yet. Please try again later.")
