from aiogram import types, Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from config.settings import PLANS, BOT_TOKEN, FORCE_SUBSCRIBE_CHANNEL_LINK
from utils.supabase_db import (
    add_subscription, get_wallet_balance, deduct_wallet, get_plan, 
    get_unused_credential, mark_credential_used, create_transaction,
    allocate_combo_credentials, update_wallet
)
from utils.log_utils import log_event
from utils.force_subscribe import is_user_subscribed
from utils.text_utils import toSmallCaps
import random
from datetime import datetime, timedelta

# YouTube Premium FSM States
class YouTubeStates(StatesGroup):
    waiting_for_email = State()
    confirming_email = State()

# YouTube Logs Channel
YT_LOGS_CHANNEL = -1002780521171


def register_ott(dp):
    # 🎬 Main OTT Menu
    @dp.callback_query_handler(lambda c: c.data == "menu_buy_otts")
    async def menu_buy_otts(callback_query: types.CallbackQuery):
        user_id = callback_query.from_user.id
        
        # Force subscribe check
        is_subscribed = await is_user_subscribed(user_id)
        if not is_subscribed:
            await callback_query.answer("⚠️ Please join our channel first!", show_alert=True)
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
        
        kb = InlineKeyboardMarkup(row_width=1)
        kb.add(
            InlineKeyboardButton(toSmallCaps("📺 Netflix 4K"), callback_data="plan_netflix"),
            InlineKeyboardButton(toSmallCaps("🎬 Prime Video"), callback_data="plan_prime"),
            InlineKeyboardButton(toSmallCaps("🎵 YouTube Premium"), callback_data="plan_youtube"),
            InlineKeyboardButton(toSmallCaps("🔥 Pornhub Premium"), callback_data="plan_pornhub"),
            InlineKeyboardButton(toSmallCaps("🎁 Combo Pack"), callback_data="plan_combo"),
            InlineKeyboardButton(toSmallCaps("⬅️ Back"), callback_data="back_to_main")
        )
        await callback_query.message.edit_text(
            toSmallCaps("<b>🎬 Choose Your OTT Platform:</b>"),
            parse_mode="HTML",
            reply_markup=kb
        )
        await callback_query.answer()

    # --- PLAN DETAILS HANDLERS ---

    @dp.callback_query_handler(lambda c: c.data == "plan_netflix")
    async def plan_netflix(callback_query: types.CallbackQuery):
        price = PLANS['netflix_4k']['price']
        text = toSmallCaps(
            f"<b>📺 NETFLIX PREMIUM 4K\n\n"
            f"• Private Screen\n"
            f"• TV/Laptop Supported\n"
            f"• 4K + HDR\n"
            f"• Price : 75₹ / Month\n\n"
            f"🕒 Validity: 1 Month\n"
            f"💳 PRICE: ₹{price}</b>"
        )
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton(toSmallCaps("💰 Buy Now"), callback_data="buy:netflix_4k"))
        kb.add(InlineKeyboardButton(toSmallCaps("⬅️ Back"), callback_data="menu_buy_otts"))
        await callback_query.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
        await callback_query.answer()

    @dp.callback_query_handler(lambda c: c.data == "plan_prime")
    async def plan_prime(callback_query: types.CallbackQuery):
        price = PLANS['prime_video']['price']
        text = toSmallCaps(
            f"<b>🎬 PRIME VIDEO\n\n"
            f"• Private Single Screen\n"
            f"• HD 1080p\n"
            f"• No ads\n"
            f"• Price : 35₹/Month\n\n"
            f"🕒 Validity: 1 Month\n"
            f"💳 PRICE: ₹{price}</b>"
        )
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton(toSmallCaps("💰 Buy Now"), callback_data="buy:prime_video"))
        kb.add(InlineKeyboardButton(toSmallCaps("⬅️ Back"), callback_data="menu_buy_otts"))
        await callback_query.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
        await callback_query.answer()

    @dp.callback_query_handler(lambda c: c.data == "plan_youtube")
    async def plan_youtube(callback_query: types.CallbackQuery):
        price = PLANS['youtube']['price']
        text = toSmallCaps(
            f"<b>▶️ YOUTUBE PREMIUM\n\n"
            f"• No Ads\n"
            f"• Background Play\n"
            f"• YouTube Music\n"
            f"• On your mail\n"
            f"• Price 25₹/ Month\n\n"
            f"🕒 Validity: 1 Month\n"
            f"💳 PRICE: ₹{price}</b>"
        )
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton(toSmallCaps("💰 Buy Now"), callback_data="buy:youtube"))
        kb.add(InlineKeyboardButton(toSmallCaps("⬅️ Back"), callback_data="menu_buy_otts"))
        await callback_query.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
        await callback_query.answer()

    @dp.callback_query_handler(lambda c: c.data == "plan_pornhub")
    async def plan_pornhub(callback_query: types.CallbackQuery):
        price = PLANS['pornhub']['price']
        text = toSmallCaps(
            f"<b>🔥 PORNHUB PREMIUM\n\n"
            f"✅ Private Single Screen\n"
            f"💎 Max Quality (1080p/4K)\n"
            f"💻 TV / PC / Mobile Supported\n"
            f"🕒 Validity: 1 Month\n"
            f"💳 PRICE: ₹{price}</b>"
        )
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton(toSmallCaps("💰 Buy Now"), callback_data="buy:pornhub"))
        kb.add(InlineKeyboardButton(toSmallCaps("⬅️ Back"), callback_data="menu_buy_otts"))
        await callback_query.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
        await callback_query.answer()

    @dp.callback_query_handler(lambda c: c.data == "plan_combo")
    async def plan_combo(callback_query: types.CallbackQuery):
        price = PLANS['combo']['price']
        text = toSmallCaps(
            f"<b>🎁 OTT COMBO PACK\n\n"
            f"📺 NETFLIX PREMIUM 4K\n"
            f"• Private Screen\n"
            f"• TV/Laptop Supported\n"
            f"• 4K + HDR\n"
            f"• Price: 75₹ / Month\n\n"
            f"🎬 PRIME VIDEO\n"
            f"• Private Single Screen\n"
            f"• HD 1080p\n"
            f"• No ads\n"
            f"• Price: 35₹/Month\n\n"
            f"▶️ YOUTUBE PREMIUM\n"
            f"• No Ads\n"
            f"• Background Play\n"
            f"• YouTube Music\n"
            f"• On your mail\n"
            f"• Price: 25₹/ Month\n\n"
            f"+\n\n"
            f"🔞 FREE: PORNHUB PREMIUM\n"
            f"• Full Access\n"
            f"• HD Quality (free with combo)\n\n"
            f"🕒 Validity: 1 Month\n"
            f"💳 PRICE: ₹{price}</b>"
        )
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton(toSmallCaps("💰 Buy Now"), callback_data="buy:combo"))
        kb.add(InlineKeyboardButton(toSmallCaps("⬅️ Back"), callback_data="menu_buy_otts"))
        await callback_query.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
        await callback_query.answer()

    # --- PURCHASE HANDLER ---

    @dp.callback_query_handler(lambda c: c.data and c.data.startswith("buy:"), state="*")
    async def buy_callback(callback_query: types.CallbackQuery, state: FSMContext):
        _, plan_key = callback_query.data.split(":", 1)
        plan = PLANS.get(plan_key)
        uid = callback_query.from_user.id
        username = callback_query.from_user.username or "NoUsername"

        if not plan:
            await callback_query.answer("❌ Invalid plan selection.", show_alert=True)
            return

        # Check if plan exists in new system
        db_plan = get_plan(plan_key)
        if not db_plan:
            await callback_query.answer("❌ Plan not available", show_alert=True)
            return
        
        # Check if plan is active
        if not db_plan.get("active", True):
            await callback_query.message.answer(
                toSmallCaps("<b>❌ This Plan Is Currently Unavailable. Please Try Again Later.</b>"),
                parse_mode="HTML"
            )
            await callback_query.answer()
            return
        
        # SPECIAL FLOW FOR YOUTUBE PREMIUM
        if plan_key == "youtube":
            price = plan["price"]
            bal = get_wallet_balance(uid)

            if bal < price:
                await callback_query.message.answer(
                    toSmallCaps("<b>❌ Insufficient Wallet Balance! Please Add Funds First.</b>"),
                    parse_mode="HTML"
                )
                await callback_query.answer()
                return

            # Deduct wallet
            success = deduct_wallet(uid, price)
            if not success:
                await callback_query.message.answer(
                    toSmallCaps("<b>⚠️ Wallet Deduction Failed. Try Again.</b>"),
                    parse_mode="HTML"
                )
                await callback_query.answer()
                return

            # Save purchase info and ask for email
            order_id = f"YOUTUBE{random.randint(1000, 9999)}"
            await state.update_data(
                plan_key=plan_key,
                order_id=order_id,
                price=price,
                username=username
            )
            await YouTubeStates.waiting_for_email.set()
            
            await callback_query.message.answer(
                toSmallCaps(
                    "<b>📺 YOUTUBE PREMIUM:\n"
                    "📧 Please send your Gmail ID for automatic family addition\n"
                    "⚠️ Must be fresh Gmail (no family joined)\n"
                    "🎯 You will be automatically added to our family account!</b>"
                ),
                parse_mode="HTML"
            )
            await callback_query.answer()
            return
        
        # SPECIAL FLOW FOR COMBO PLAN
        if plan_key == "combo":
            price = plan["price"]
            bal = get_wallet_balance(uid)

            if bal < price:
                await callback_query.message.answer(
                    toSmallCaps("<b>❌ Insufficient Wallet Balance! Please Add Funds First.</b>"),
                    parse_mode="HTML"
                )
                await callback_query.answer()
                return

            # Deduct wallet first
            success = deduct_wallet(uid, price)
            if not success:
                await callback_query.message.answer(
                    toSmallCaps("<b>⚠️ Wallet Deduction Failed. Try Again.</b>"),
                    parse_mode="HTML"
                )
                await callback_query.answer()
                return

            # Allocate combo credentials atomically
            result = allocate_combo_credentials(uid)
            
            if not result["success"]:
                # Refund if allocation failed
                update_wallet(uid, price)
                missing = ", ".join(result["missing_stock"])
                await callback_query.message.answer(
                    toSmallCaps(
                        f"<b>❌ Combo Plan Unavailable!\n\n"
                        f"Out of stock: {missing}\n\n"
                        f"Your wallet has been refunded.\n"
                        f"Please try again later.</b>"
                    ),
                    parse_mode="HTML"
                )
                await log_event("PURCHASE_FAILED", {
                    "user_id": uid,
                    "name": message.from_user.full_name,
                    "username": username,
                    "plan_name": "Combo Plan",
                    "reason": f"Out of stock - Missing: {missing}"
                })
                await callback_query.answer()
                return

            # Create transaction
            create_transaction(uid, "Combo Plan Purchase", -price, "purchase")
            
            # Calculate dates
            start_date = datetime.now()
            end_date = start_date + timedelta(days=30)
            start_str = start_date.strftime("%d %B %Y").upper()
            end_str = end_date.strftime("%d %B %Y").upper()

            # Build message for regular services (Netflix, Prime, Pornhub)
            credentials = result["credentials"]
            message_parts = [toSmallCaps("<b>🎉 YOUR COMBO PLAN CREDENTIALS:\n")]
            
            plan_names = {
                "netflix_4k": "📺 Netflix 4K",
                "prime_video": "🎬 Prime Video",
                "pornhub": "🔞 Pornhub Premium"
            }
            
            for plan_key, credential in credentials.items():
                cred_parts = credential.split(":")
                email = cred_parts[0].strip() if len(cred_parts) > 0 else "N/A"
                password = cred_parts[1].strip() if len(cred_parts) > 1 else "N/A"
                
                plan_name = plan_names.get(plan_key, plan_key.upper())
                message_parts.append(
                    f"\n{toSmallCaps(plan_name)}\n"
                    f"{toSmallCaps('📧 ID')}: <code>{email}</code>\n"
                    f"{toSmallCaps('🔑 Password')}: <code>{password}</code>\n"
                )
            
            dont_change_text = toSmallCaps("DON'T CHANGE PASSWORD OR LOCK PROFILE!")
            message_parts.append(
                f"\n{dont_change_text}\n\n"
                f"{toSmallCaps('⏰ STARTS')}: {start_str}\n"
                f"{toSmallCaps('✅ ENDS')}: {end_str}</b>"
            )
            
            # Send regular services credentials
            await callback_query.message.answer(
                "".join(message_parts),
                parse_mode="HTML"
            )

            # Send balance deduction message
            new_balance = get_wallet_balance(uid)
            await callback_query.message.answer(
                f"<b>{toSmallCaps('💰 BALANCE DEDUCTED')}: ₹{price}\n"
                f"{toSmallCaps('💵 UPDATED BALANCE')}: ₹{new_balance}</b>",
                parse_mode="HTML"
            )
            
            # If YouTube is in combo, trigger YouTube email collection flow
            if result["youtube_separate"]:
                order_id = f"YOUTUBE{random.randint(1000, 9999)}"
                await state.update_data(
                    plan_key="youtube",
                    order_id=order_id,
                    price=0,  # Already paid as part of combo
                    username=username,
                    is_combo=True
                )
                await YouTubeStates.waiting_for_email.set()
                
                await callback_query.message.answer(
                    toSmallCaps(
                        "<b>📺 YOUTUBE PREMIUM (COMBO):\n"
                        "📧 Please send your Gmail ID for automatic family addition\n"
                        "⚠️ Must be fresh Gmail (no family joined)\n"
                        "🎯 You will be automatically added to our family account!</b>"
                    ),
                    parse_mode="HTML"
                )
            else:
                # Send feedback message
                feedback_kb = InlineKeyboardMarkup(row_width=1)
                feedback_kb.add(
                    InlineKeyboardButton(
                        toSmallCaps("📸 Send Feedback Screenshot"),
                        url="https://t.me/Ottsonly1"
                    )
                )
                await callback_query.message.answer(
                    toSmallCaps(
                        f"<b>Send feedback + screenshot to get 24/7 support if any issue occurs\n"
                        f"and get up to 10% off for next order</b>"
                    ),
                    parse_mode="HTML",
                    reply_markup=feedback_kb
                )

            # Log combo purchase
            await log_event("PURCHASE_SUCCESS", {
                "user_id": uid,
                "name": message.from_user.full_name,
                "username": username,
                "plan_name": "Combo Plan",
                "price": price
            })
            
            await callback_query.answer()
            return
        
        # Regular flow for other plans
        # Check stock availability
        credential = get_unused_credential(plan_key)
        if not credential:
            await callback_query.message.answer(
                toSmallCaps("<b>❌ Out Of Stock!\n\nThis Plan Is Temporarily Unavailable. Please Check Back Later.</b>"),
                parse_mode="HTML"
            )
            await log_event("PURCHASE_FAILED", {
                "user_id": uid,
                "name": callback_query.from_user.full_name,
                "username": username,
                "plan_name": db_plan['ott_name'],
                "reason": "Out of stock"
            })
            await callback_query.answer()
            return

        price = plan["price"]
        bal = get_wallet_balance(uid)

        if bal < price:
            await callback_query.message.answer(
                toSmallCaps("<b>❌ Insufficient Wallet Balance! Please Add Funds First.</b>"),
                parse_mode="HTML"
            )
            await log_event("PURCHASE_FAILED", {
                "user_id": uid,
                "name": callback_query.from_user.full_name,
                "username": username,
                "plan_name": plan['name'],
                "reason": f"Insufficient balance - Has ₹{bal}, needs ₹{price}"
            })
            await callback_query.answer()
            return

        # Deduct wallet
        success = deduct_wallet(uid, price)
        if not success:
            await callback_query.message.answer(toSmallCaps("<b>⚠️ Wallet Deduction Failed. Try Again.</b>"), parse_mode="HTML")
            await callback_query.answer()
            return

        # Mark credential as used
        mark_credential_used(plan_key, credential, uid)
        
        # Add subscription
        add_subscription(uid, plan_key)
        new_balance = get_wallet_balance(uid)
        order_id = f"{plan_key.upper()}{random.randint(1000, 9999)}"

        # Calculate dates
        start_date = datetime.now()
        end_date = start_date + timedelta(days=30)
        start_str = start_date.strftime("%d %B %Y").upper()
        end_str = end_date.strftime("%d %B %Y").upper()

        # Parse credentials
        cred_parts = credential.split(":")
        email = cred_parts[0].strip() if len(cred_parts) > 0 else "N/A"
        password = cred_parts[1].strip() if len(cred_parts) > 1 else "N/A"

        # Send credentials to user
        dont_change_text = toSmallCaps("DON'T CHANGE PASSWORD OR LOCK PROFILE!")
        await callback_query.message.answer(
            f"<b>{toSmallCaps('🎉 YOUR SUBSCRIPTION DETAILS:')}\n\n"
            f"{toSmallCaps('📧')}: <code>{email}</code>\n"
            f"{toSmallCaps('🔑')}: <code>{password}</code>\n\n"
            f"{dont_change_text}\n\n"
            f"{toSmallCaps('⏰ STARTS')}: {start_str}\n"
            f"{toSmallCaps('✅ ENDS')}: {end_str}</b>",
            parse_mode="HTML"
        )

        # Send balance deduction message
        await callback_query.message.answer(
            f"<b>{toSmallCaps('💰 BALANCE DEDUCTED')}: ₹{price}\n"
            f"{toSmallCaps('💵 UPDATED BALANCE')}: ₹{new_balance}</b>",
            parse_mode="HTML"
        )

        # Send feedback message with button
        feedback_kb = InlineKeyboardMarkup(row_width=1)
        feedback_kb.add(
            InlineKeyboardButton(
                toSmallCaps("📸 Send Feedback Screenshot"),
                url="https://t.me/Ottsonly1"
            )
        )
        await callback_query.message.answer(
            toSmallCaps(
                f"<b>Send feedback + screenshot to get 24/7 support if any issue occurs\n"
                f"and get up to 10% off for next order</b>"
            ),
            parse_mode="HTML",
            reply_markup=feedback_kb
        )

        await log_event("PURCHASE_SUCCESS", {
            "user_id": uid,
            "name": callback_query.from_user.full_name,
            "username": username,
            "plan_name": plan['name'],
            "price": price
        })
        await callback_query.answer()


    # --- BACK TO MAIN MENU ---
    @dp.callback_query_handler(lambda c: c.data == "back_to_main", state="*")
    async def back_to_main(callback: types.CallbackQuery, state: FSMContext):
        await state.finish()
        kb = InlineKeyboardMarkup(row_width=1)
        kb.add(
            InlineKeyboardButton(toSmallCaps("💳 Add Funds"), callback_data="add_funds"),
            InlineKeyboardButton(toSmallCaps("🎬 Buy OTT Subscriptions"), callback_data="menu_buy_otts"),
            InlineKeyboardButton(toSmallCaps("🎁 Refer & Earn"), callback_data="refer"),
            InlineKeyboardButton(toSmallCaps("⚙️ Settings"), callback_data="menu_settings")
        )
        await callback.message.edit_text(
            toSmallCaps("<b>🏠 Main Menu - Choose An Option Below:</b>"),
            parse_mode="HTML",
            reply_markup=kb
        )
        await callback.answer()

    # ========== YOUTUBE PREMIUM EMAIL COLLECTION ==========
    
    @dp.message_handler(state=YouTubeStates.waiting_for_email)
    async def youtube_email_received(message: types.Message, state: FSMContext):
        email = message.text.strip()
        
        # Save email and show confirmation
        await state.update_data(email=email)
        await YouTubeStates.confirming_email.set()
        
        kb = InlineKeyboardMarkup(row_width=2)
        kb.add(
            InlineKeyboardButton(toSmallCaps("✅ Confirm"), callback_data="yt_confirm_email"),
            InlineKeyboardButton(toSmallCaps("✏️ Edit Mail"), callback_data="yt_edit_email")
        )
        
        await message.answer(
            f"<b>{toSmallCaps('📧 YOUR EMAIL:')}\n\n<code>{email}</code></b>",
            parse_mode="HTML",
            reply_markup=kb
        )
    
    @dp.callback_query_handler(lambda c: c.data == "yt_edit_email", state=YouTubeStates.confirming_email)
    async def youtube_edit_email(callback: types.CallbackQuery, state: FSMContext):
        await YouTubeStates.waiting_for_email.set()
        
        await callback.message.edit_text(
            toSmallCaps(
                "<b>📺 YOUTUBE PREMIUM:\n"
                "📧 Please send your Gmail ID for automatic family addition\n"
                "⚠️ Must be fresh Gmail (no family joined)\n"
                "🎯 You will be automatically added to our family account!</b>"
            ),
            parse_mode="HTML"
        )
        await callback.answer()
    
    @dp.callback_query_handler(lambda c: c.data == "yt_confirm_email", state=YouTubeStates.confirming_email)
    async def youtube_confirm_email(callback: types.CallbackQuery, state: FSMContext):
        data = await state.get_data()
        email = data.get("email")
        order_id = data.get("order_id")
        price = data.get("price", 0)
        username = data.get("username")
        is_combo = data.get("is_combo", False)
        uid = callback.from_user.id
        
        # Add subscription only if not already added (combo adds it earlier)
        if not is_combo:
            add_subscription(uid, "youtube")
        
        # Create transaction only if standalone purchase (not combo)
        if not is_combo and price > 0:
            create_transaction(uid, "YouTube Premium Purchase", -price, "purchase")
        
        # Send confirmation to user
        await callback.message.edit_text(
            toSmallCaps(
                f"<b>✅ {email} has been submitted for premium!\n\n"
                f"We will invite you into our premium family and let you know.\n"
                f"Usually takes 30 mins.\n\n"
                f"We will update here.</b>"
            ),
            parse_mode="HTML"
        )
        
        # Send to YouTube logs channel
        bot = Bot(token=BOT_TOKEN)
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton(
            toSmallCaps("✅ Done"),
            callback_data=f"yt_done_{uid}_{email}_{username}"
        ))
        
        purchase_type = "COMBO" if is_combo else "INDIVIDUAL"
        log_text = (
            f"<b>{toSmallCaps('⚠️ MANUAL YOUTUBE PREMIUM REQUEST')}\n\n"
            f"{toSmallCaps('👤 USER')}: <code>{uid}</code>\n"
            f"{toSmallCaps('📛 USERNAME')}: @{username}\n"
            f"{toSmallCaps('📧 EMAIL')}: <code>{email}</code>\n"
            f"{toSmallCaps('🆔 ORDER ID')}: {toSmallCaps(order_id)}\n"
            f"{toSmallCaps('💰 AMOUNT')}: {toSmallCaps(f'₹{price}')}\n"
            f"{toSmallCaps('🔖 TYPE')}: {toSmallCaps(purchase_type)}\n"
            f"{toSmallCaps('📅 TIME')}: {toSmallCaps(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}</b>"
        )
        
        await bot.send_message(YT_LOGS_CHANNEL, log_text, parse_mode="HTML", reply_markup=kb)
        
        await state.finish()
        await callback.answer()
    
    @dp.callback_query_handler(lambda c: c.data and c.data.startswith("yt_done_"), state="*")
    async def youtube_done_admin(callback: types.CallbackQuery):
        parts = callback.data.split("_", 3)  # Split into max 4 parts
        user_id = int(parts[2])
        
        # Extract email and username from callback_data
        remaining = parts[3]
        email_and_username = remaining.rsplit("_", 1)  # Split from the end to get username
        email = email_and_username[0] if len(email_and_username) > 1 else "N/A"
        username = email_and_username[1] if len(email_and_username) > 1 else "NoUsername"
        
        # Edit the logs channel message
        await callback.message.edit_text(
            f"<b>{toSmallCaps('✅ PREMIUM WAS SENT TO')} @{username}\n"
            f"{toSmallCaps('MAIL')}: <code>{email}</code></b>",
            parse_mode="HTML"
        )
        
        # Send message to user
        bot = Bot(token=BOT_TOKEN)
        await bot.send_message(
            user_id,
            toSmallCaps(
                "<b>✅ We have invited you into your YouTube Premium family!\n"
                "Go to your mail and accept the invitation.\n\n"
                "Thank you! Send screenshot for feedback.</b>"
            ),
            parse_mode="HTML"
        )
        
        # Send feedback message button
        feedback_kb = InlineKeyboardMarkup(row_width=1)
        feedback_kb.add(
            InlineKeyboardButton(
                toSmallCaps("📸 Send Feedback Screenshot"),
                url="https://t.me/Ottsonly1"
            )
        )
        await bot.send_message(
            user_id,
            toSmallCaps(
                f"<b>Send feedback + screenshot to get 24/7 support if any issue occurs\n"
                f"and get up to 10% off for next order</b>"
            ),
            parse_mode="HTML",
            reply_markup=feedback_kb
        )
        
        await callback.answer("✅ User notified!")

