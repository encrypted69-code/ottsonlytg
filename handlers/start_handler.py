from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.supabase_db import create_user_if_not_exists, get_user
from utils.log_utils import log_event
from utils.force_subscribe import is_user_subscribed
from config.settings import REFERRAL_BASE_URL, FORCE_SUBSCRIBE_CHANNEL_LINK
from utils.text_utils import toSmallCaps


def register_start(dp):
    """
    Handles /start command, main menu, and referral system.
    """

    # ========== START COMMAND ==========
    @dp.message_handler(commands=["start"])
    async def start_command(message: types.Message):
        user_id = message.from_user.id
        name = message.from_user.full_name
        username = message.from_user.username
        
        # ============================================
        # FORCE SUBSCRIBE CHECK
        # ============================================
        
        # Check if user is subscribed to the channel
        is_subscribed = await is_user_subscribed(user_id)
        
        if not is_subscribed:
            # Show force subscribe message
            force_subscribe_text = (
                "👋 Hi, I am OTTSONLY Bot\n\n"
                "Here you can get YouTube Premium at just ₹25.\n\n"
                "👉 Join our official channel to access this store."
            )
            
            # Create keyboard with Join Channel and Verify buttons
            kb = InlineKeyboardMarkup(row_width=1)
            kb.add(
                InlineKeyboardButton("📢 JOIN CHANNEL", url=FORCE_SUBSCRIBE_CHANNEL_LINK),
                InlineKeyboardButton("✅ VERIFY", callback_data="verify_subscription")
            )
            
            await message.answer(force_subscribe_text, reply_markup=kb)
            return
        
        # ============================================
        # USER IS SUBSCRIBED - CONTINUE NORMAL FLOW
        # ============================================
        
        # Check for referral ID
        args = message.get_args()

        # Check if user exists
        existing_user = get_user(user_id)
        is_new_user = existing_user is None

        # Create user if not exists
        user = create_user_if_not_exists(user_id, name)

        # Handle referral (if any)
        if args and args.isdigit():
            referrer_id = int(args)
            if referrer_id != user_id and not user.get("referred_by"):
                from utils.supabase_db import set_referred_by, get_user as get_referrer
                set_referred_by(user_id, referrer_id)
                
                # Get referrer info
                referrer = get_referrer(referrer_id)
                referrer_name = referrer.get("name", "Unknown") if referrer else "Unknown"
                
                # Log referral join
                await log_event("REFERRAL_JOIN", {
                    "user_id": user_id,
                    "name": name,
                    "username": username,
                    "referrer_id": referrer_id,
                    "referrer_name": referrer_name
                })

        # Referral link for user
        referral_link = f"{REFERRAL_BASE_URL}{user_id}"

        # Welcome message
        welcome_text = toSmallCaps(
            f"<b>Welcome to ottsonly, {name}\n"
            f"🚀 OTT SUBSCRIPTIONS AT BEST PRICES\n"
            f"Netflix • Prime • YouTube • Spotify & more\n\n"
            f"⚡ Instant access\n"
            f"🔒 100% trusted\n"
            f"💎 Premium quality</b>"
        )

        # Inline keyboard
        kb = InlineKeyboardMarkup(row_width=2)
        kb.add(
            InlineKeyboardButton(toSmallCaps("💳 Add Funds"), callback_data="menu_add_funds"),
            InlineKeyboardButton(toSmallCaps("🎬 Buy OTTs"), callback_data="menu_buy_otts"),
            InlineKeyboardButton(toSmallCaps("🎁 Refer & Earn"), callback_data="menu_refer"),
            InlineKeyboardButton(toSmallCaps("👤 Profile"), callback_data="menu_profile"),
            InlineKeyboardButton(toSmallCaps("📚 Tutorial"), url="https://t.me/+yEMiVMf-mkBmOWE1"),
            InlineKeyboardButton(toSmallCaps("💬 Support"), url="https://t.me/ottsonly1")
        )

        await message.answer(welcome_text, parse_mode="HTML", reply_markup=kb)
        # Removed noisy /start log - only log referral joins


    # ========== VERIFY SUBSCRIPTION CALLBACK ==========
    @dp.callback_query_handler(lambda c: c.data == "verify_subscription")
    async def verify_subscription(callback_query: types.CallbackQuery):
        user_id = callback_query.from_user.id
        name = callback_query.from_user.full_name
        
        # Check if user is now subscribed
        is_subscribed = await is_user_subscribed(user_id)
        
        if is_subscribed:
            # ✅ User has joined - grant access
            await callback_query.answer("✅ Verified! Welcome to OTTSONLY!", show_alert=True)
            
            # Create user if not exists
            create_user_if_not_exists(user_id, name)
            
            # Show main menu
            welcome_text = toSmallCaps(
                f"<b>Welcome to ottsonly, {name}\n"
                f"🚀 OTT SUBSCRIPTIONS AT BEST PRICES\n"
                f"Netflix • Prime • YouTube • Spotify & more\n\n"
                f"⚡ Instant access\n"
                f"🔒 100% trusted\n"
                f"💎 Premium quality</b>"
            )
            
            kb = InlineKeyboardMarkup(row_width=2)
            kb.add(
                InlineKeyboardButton(toSmallCaps("💳 Add Funds"), callback_data="menu_add_funds"),
                InlineKeyboardButton(toSmallCaps("🎬 Buy OTTs"), callback_data="menu_buy_otts"),
                InlineKeyboardButton(toSmallCaps("🎁 Refer & Earn"), callback_data="menu_refer"),
                InlineKeyboardButton(toSmallCaps("👤 Profile"), callback_data="menu_profile"),
                InlineKeyboardButton(toSmallCaps("📚 Tutorial"), url="https://t.me/+yEMiVMf-mkBmOWE1"),
                InlineKeyboardButton(toSmallCaps("💬 Support"), url="https://t.me/ottsonly1")
            )
            
            await callback_query.message.edit_text(welcome_text, parse_mode="HTML", reply_markup=kb)
            
        else:
            # ❌ User has NOT joined yet
            await callback_query.answer(
                "❌ Access denied.\n\nPlease join our channel first to use this bot.",
                show_alert=True
            )
            
            # Keep showing the same Join + Verify buttons
            force_subscribe_text = (
                "👋 Hi, I am OTTSONLY Bot\n\n"
                "Here you can get YouTube Premium at just ₹25.\n\n"
                "👉 Join our official channel to access this store."
            )
            
            kb = InlineKeyboardMarkup(row_width=1)
            kb.add(
                InlineKeyboardButton("📢 JOIN CHANNEL", url=FORCE_SUBSCRIBE_CHANNEL_LINK),
                InlineKeyboardButton("✅ VERIFY", callback_data="verify_subscription")
            )
            
            await callback_query.message.edit_text(force_subscribe_text, reply_markup=kb)

    # ========== BACK TO MAIN MENU ==========
    @dp.callback_query_handler(lambda c: c.data == "back_to_main")
    async def back_to_main(callback_query: types.CallbackQuery):
        user_id = callback_query.from_user.id
        
        # Force subscribe check
        is_subscribed = await is_user_subscribed(user_id)
        if not is_subscribed:
            force_subscribe_text = (
                "👋 Hi, I am OTTSONLY Bot\n\n"
                "Here you can get YouTube Premium at just ₹25.\n\n"
                "👉 Join our official channel to access this store."
            )
            kb = InlineKeyboardMarkup(row_width=1)
            kb.add(
                InlineKeyboardButton("📢 JOIN CHANNEL", url=FORCE_SUBSCRIBE_CHANNEL_LINK),
                InlineKeyboardButton("✅ VERIFY", callback_data="verify_subscription")
            )
            await callback_query.message.edit_text(force_subscribe_text, reply_markup=kb)
            return
        
        # Show main menu
        kb = InlineKeyboardMarkup(row_width=2)
        kb.add(
            InlineKeyboardButton(toSmallCaps("💳 Add Funds"), callback_data="menu_add_funds"),
            InlineKeyboardButton(toSmallCaps("🎬 Buy OTT Subscriptions"), callback_data="menu_buy_otts"),
            InlineKeyboardButton(toSmallCaps("🎁 Refer & Earn"), callback_data="menu_refer"),
            InlineKeyboardButton(toSmallCaps("👤 Profile"), callback_data="menu_profile"),
            InlineKeyboardButton(toSmallCaps("📚 Tutorial"), url="https://t.me/+yEMiVMf-mkBmOWE1"),
            InlineKeyboardButton(toSmallCaps("💬 Support"), url="https://t.me/ottsonly1")
        )
        await callback_query.message.edit_text(
            toSmallCaps("<b>🏠 Main Menu — Choose An Option Below:</b>"),
            parse_mode="HTML",
            reply_markup=kb
        )
        await callback_query.answer()
