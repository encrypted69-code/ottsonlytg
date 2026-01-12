from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.supabase_db import get_user, get_referral_stats
from utils.text_utils import toSmallCaps
from config.settings import REFERRAL_BASE_URL


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
        # Removed noisy profile view log

        await callback_query.answer()


    # ========== REFER & EARN MENU ==========
    @dp.callback_query_handler(lambda c: c.data == "menu_refer")
    async def menu_refer(callback_query: types.CallbackQuery):
        user_id = callback_query.from_user.id
        user = get_user(user_id)

        if not user:
            await callback_query.message.answer(
                toSmallCaps("<b>⚠️ Profile Not Found. Please Use /start To Register.</b>"), 
                parse_mode="HTML"
            )
            await callback_query.answer()
            return

        # Get referral stats
        stats = get_referral_stats(user_id)
        total_referrals = stats.get("total_referrals", 0)
        total_earnings = stats.get("total_earnings", 0)
        pending_earnings = stats.get("pending_earnings", 0)

        # Referral link
        referral_link = f"{REFERRAL_BASE_URL}{user_id}"

        # Refer & Earn message
        refer_text = toSmallCaps(
            f"<b>🎁 Refer & Earn Program\n\n"
            f"💰 Earn Up To ₹37 Per Referral!\n\n"
            f"📊 Your Stats:\n"
            f"👥 Total Referrals: {total_referrals}\n"
            f"💵 Total Earned: ₹{total_earnings:.2f}\n"
            f"⏳ Pending: ₹{pending_earnings:.2f}\n\n"
            f"🔗 Your Referral Link:\n"
            f"{referral_link}\n\n"
            f"📖 How It Works:\n"
            f"1️⃣ Share Your Link With Friends\n"
            f"2️⃣ They Buy OTT Subscription (₹135)\n"
            f"3️⃣ You Earn ₹28 Instantly!\n"
            f"4️⃣ Your Referrals Refer Someone → You Get ₹9 More!\n\n"
            f"💡 2-Level Earning System:\n"
            f"• Level 1: 30% (₹28) - Direct Referrals\n"
            f"• Level 2: 10% (₹9) - Indirect Referrals\n\n"
            f"⚡ Earnings Are Credited After 24 Hours\n"
            f"💸 Withdraw Anytime (Min: ₹100)</b>"
        )

        # Inline buttons
        kb = InlineKeyboardMarkup(row_width=1)
        kb.add(
            InlineKeyboardButton(toSmallCaps("📊 View Detailed Stats"), callback_data="refer_stats"),
            InlineKeyboardButton(toSmallCaps("💸 Withdraw Earnings"), callback_data="refer_withdraw"),
            InlineKeyboardButton(toSmallCaps("📤 Share Link"), switch_inline_query=f"Join OTTsOnly & Get Premium OTT Subscriptions! Use My Link: {referral_link}")
        )
        kb.add(InlineKeyboardButton(toSmallCaps("⬅️ Back to Menu"), callback_data="back_to_main"))

        await callback_query.message.edit_text(refer_text, parse_mode="HTML", reply_markup=kb)
        await callback_query.answer()


    # ========== DETAILED REFERRAL STATS ==========
    @dp.callback_query_handler(lambda c: c.data == "refer_stats")
    async def refer_stats(callback_query: types.CallbackQuery):
        user_id = callback_query.from_user.id
        stats = get_referral_stats(user_id)

        level1_count = stats.get("level1_referrals", 0)
        level2_count = stats.get("level2_referrals", 0)
        level1_buyers = stats.get("level1_buyers", 0)
        level2_buyers = stats.get("level2_buyers", 0)
        total_earnings = stats.get("total_earnings", 0)
        pending_earnings = stats.get("pending_earnings", 0)
        withdrawable = stats.get("withdrawable_earnings", 0)

        stats_text = toSmallCaps(
            f"<b>📊 Detailed Referral Statistics\n\n"
            f"👥 Level 1 Referrals:\n"
            f"• Total Signups: {level1_count}\n"
            f"• Buyers: {level1_buyers}\n"
            f"• Earnings: ₹{level1_buyers * 28:.2f}\n\n"
            f"👥 Level 2 Referrals:\n"
            f"• Total Signups: {level2_count}\n"
            f"• Buyers: {level2_buyers}\n"
            f"• Earnings: ₹{level2_buyers * 9:.2f}\n\n"
            f"💰 Earnings Breakdown:\n"
            f"• Total Earned: ₹{total_earnings:.2f}\n"
            f"• Pending (24h Hold): ₹{pending_earnings:.2f}\n"
            f"• Ready to Withdraw: ₹{withdrawable:.2f}\n\n"
            f"🎯 Conversion Rate: {(level1_buyers / level1_count * 100 if level1_count > 0 else 0):.1f}%</b>"
        )

        kb = InlineKeyboardMarkup(row_width=1)
        kb.add(
            InlineKeyboardButton(toSmallCaps("💸 Withdraw Now"), callback_data="refer_withdraw"),
            InlineKeyboardButton(toSmallCaps("⬅️ Back"), callback_data="menu_refer")
        )

        await callback_query.message.edit_text(stats_text, parse_mode="HTML", reply_markup=kb)
        await callback_query.answer()


    # ========== WITHDRAW EARNINGS ==========
    @dp.callback_query_handler(lambda c: c.data == "refer_withdraw")
    async def refer_withdraw(callback_query: types.CallbackQuery):
        user_id = callback_query.from_user.id
        stats = get_referral_stats(user_id)
        withdrawable = stats.get("withdrawable_earnings", 0)

        if withdrawable < 100:
            await callback_query.answer(
                f"⚠️ Minimum Withdrawal: ₹100\nYou Have: ₹{withdrawable:.2f}", 
                show_alert=True
            )
            return

        withdraw_text = toSmallCaps(
            f"<b>💸 Withdraw Referral Earnings\n\n"
            f"💰 Available Balance: ₹{withdrawable:.2f}\n\n"
            f"📝 To Request Withdrawal:\n"
            f"1️⃣ Click Request Withdrawal Below\n"
            f"2️⃣ Provide Your UPI ID\n"
            f"3️⃣ We'll Process Within 24 Hours\n\n"
            f"⚠️ Minimum: ₹100\n"
            f"⚡ Processing Time: 24-48 Hours</b>"
        )

        kb = InlineKeyboardMarkup(row_width=1)
        kb.add(
            InlineKeyboardButton(toSmallCaps("✅ Request Withdrawal"), callback_data="refer_withdraw_request"),
            InlineKeyboardButton(toSmallCaps("⬅️ Back"), callback_data="menu_refer")
        )

        await callback_query.message.edit_text(withdraw_text, parse_mode="HTML", reply_markup=kb)
        await callback_query.answer()


    # ========== REQUEST WITHDRAWAL ==========
    @dp.callback_query_handler(lambda c: c.data == "refer_withdraw_request")
    async def refer_withdraw_request(callback_query: types.CallbackQuery):
        await callback_query.message.answer(
            toSmallCaps(
                "<b>💸 Withdrawal Request\n\n"
                "Please Send Your UPI ID In The Format:\n\n"
                "<code>example@paytm</code>\n"
                "<code>9876543210@ybl</code>\n\n"
                "Or Reply With /cancel To Go Back</b>"
            ),
            parse_mode="HTML"
        )
        await callback_query.answer()
        # TODO: Add FSM state for collecting UPI ID
