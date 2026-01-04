from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.supabase_db import get_user, deduct_wallet, update_wallet, add_subscription
from config.settings import LOG_CHANNEL_ID
from utils.text_utils import toSmallCaps


def register_callback_handlers(dp):
    """
    Central callback handler to manage all inline button interactions.
    """

    # ✅ Handle 'Buy OTT' actions (from start_handler)
    @dp.callback_query_handler(lambda c: c.data.startswith("buy_"))
    async def handle_ott_purchase(callback: types.CallbackQuery):
        plan_key = callback.data.split("_")[1].lower()
        user_id = callback.from_user.id
        username = callback.from_user.username or "N/A"

        # OTT Plan Prices
        price_map = {
            "netflix": 99,
            "youtube": 15,
            "prime": 25,
            "pornhub": 69
        }

        if plan_key not in price_map:
            await callback.message.answer(toSmallCaps("<b>⚠️ Invalid OTT Plan.</b>"), parse_mode="HTML")
            return

        price = price_map[plan_key]

        # Deduct wallet
        success = deduct_wallet(user_id, price)
        if not success:
            await callback.message.answer(
                toSmallCaps("<b>⚠️ Insufficient Balance!\n\nPlease Add Funds Using The Add Funds Button.</b>"),
                parse_mode="HTML"
            )
            return

        # Add subscription
        add_subscription(user_id, plan_key)
        user = get_user(user_id)
        new_balance = user.get("wallet", 0)

        # ✅ Notify user
        await callback.message.answer(
            toSmallCaps(f"<b>✅ Purchase Successful!\n\n"
            f"You Purchased {plan_key.upper()} For ₹{price}.\n"
            f"💰 Remaining Balance: ₹{new_balance}</b>"),
            parse_mode="HTML"
        )

        # 🧾 Log to admin channel
        log_message = (
            f"🎬 *OTT Purchase Log*\n\n"
            f"USER : `{user_id}`\n"
            f"USERNAME : @{username}\n"
            f"PURCHASED : {plan_key.upper()}\n"
            f"PRICE : ₹{price}\n"
            f"UPDATED BALANCE : ₹{new_balance}\n"
            f"ORDER ID : {plan_key.upper()}{user_id}"
        )
        await callback.bot.send_message(LOG_CHANNEL_ID, log_message, parse_mode="Markdown")

    # ✅ Handle "Refer" button
    @dp.callback_query_handler(lambda c: c.data == "refer")
    async def handle_refer(callback: types.CallbackQuery):
        user_id = callback.from_user.id
        refer_link = f"https://t.me/{(await callback.bot.get_me()).username}?start={user_id}"

        text = toSmallCaps(
            "<b>🎁 Refer & Earn!\n\n"
            "Invite Your Friends Using Your Referral Link Below 👇\n"
            "When They Add Funds, You'll Instantly Earn 10% Commission! 💸\n\n"
            f"🔗 Your Link: {refer_link}</b>"
        )

        kb = InlineKeyboardMarkup().add(
            InlineKeyboardButton(toSmallCaps("⬅️ Back"), callback_data="main_menu")
        )

        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb)

    # ✅ Handle "Profile" button
    @dp.callback_query_handler(lambda c: c.data == "profile")
    async def handle_profile(callback: types.CallbackQuery):
        user_id = callback.from_user.id
        user = get_user(user_id)

        if not user:
            await callback.message.answer(toSmallCaps("<b>⚠️ User Data Not Found.</b>"), parse_mode="HTML")
            return

        wallet = user.get("wallet", 0)
        subs = user.get("subscriptions", [])
        referred_by = user.get("referred_by")
        subs_text = "\n".join([f"• {s['name']} (valid till {s['expires_at'][:10]})" for s in subs]) if subs else "None"

        text = toSmallCaps(
            f"<b>👤 Your Profile\n\n"
            f"🆔 User ID: {user_id}\n"
            f"💰 Wallet Balance: ₹{wallet}\n"
            f"🎬 Active Subscriptions:\n{subs_text}\n\n"
            f"👥 Referred By: {referred_by if referred_by else 'No One'}</b>"
        )

        kb = InlineKeyboardMarkup().add(
            InlineKeyboardButton(toSmallCaps("⬅️ Back"), callback_data="main_menu")
        )

        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb)

    # ✅ Handle "Main Menu" return
    @dp.callback_query_handler(lambda c: c.data == "main_menu")
    async def handle_main_menu(callback: types.CallbackQuery):
        main_menu = InlineKeyboardMarkup(row_width=2)
        main_menu.add(
            InlineKeyboardButton(toSmallCaps("🎬 Buy OTTs"), callback_data="buy_otts"),
            InlineKeyboardButton(toSmallCaps("💰 Add Funds"), callback_data="add_funds"),
            InlineKeyboardButton(toSmallCaps("🎁 Refer"), callback_data="refer"),
            InlineKeyboardButton(toSmallCaps("👤 Profile"), callback_data="profile"),
        )
        await callback.message.edit_text(
            toSmallCaps("<b>👋 Welcome Back!\nSelect An Option Below:</b>"),
            parse_mode="HTML",
            reply_markup=main_menu
        )

    # ✅ Fallback for unknown callbacks
    @dp.callback_query_handler(lambda c: True)
    async def handle_unknown(callback: types.CallbackQuery):
        await callback.answer("⚙️ Action not recognized or expired.", show_alert=True)
