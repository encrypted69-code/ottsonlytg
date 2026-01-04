from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.supabase_db import get_user
from utils.log_utils import send_log
from utils.text_utils import toSmallCaps


def register_profile(dp):
    @dp.callback_query_handler(lambda c: c.data == "menu_profile")
    async def menu_profile(callback_query: types.CallbackQuery):
        user_id = callback_query.from_user.id
        user = get_user(user_id)

        if not user:
            await callback_query.message.answer(toSmallCaps("<b>⚠️ Profile Not Found. Please Use /start To Register.</b>"), parse_mode="HTML")
            await callback_query.answer()
            return

        name = user.get("name", "Unknown User")
        wallet = user.get("wallet", 0)
        joined_at = user.get("joined_at", "Unknown Date")
        subscriptions = user.get("subscriptions", [])
        total_subs = len(subscriptions)

        # Profile details
        profile_text = toSmallCaps(
            f"<b>👤 Your Profile\n\n"
            f"🧾 Name: {name}\n"
            f"🆔 User ID: {user_id}\n"
            f"💰 Wallet Balance: ₹{wallet}\n"
            f"🎬 Active Subscriptions: {total_subs}\n"
            f"📅 Joined: {joined_at}</b>"
        )

        # Inline buttons
        kb = InlineKeyboardMarkup(row_width=2)
        kb.add(
            InlineKeyboardButton(toSmallCaps("💳 Add Funds"), callback_data="menu_add_funds"),
            InlineKeyboardButton(toSmallCaps("🎬 Buy OTT"), callback_data="menu_buy_otts")
        )
        kb.add(InlineKeyboardButton(toSmallCaps("⬅️ Back to Menu"), callback_data="back_to_main"))

        await callback_query.message.edit_text(profile_text, parse_mode="HTML", reply_markup=kb)

        # Log profile view
        await send_log(f"👤 *Profile Viewed*\nUser: `{user_id}` | Wallet: ₹{wallet}")

        await callback_query.answer()
