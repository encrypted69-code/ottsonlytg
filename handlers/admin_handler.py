from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config.settings import ADMINS, PLANS
from utils.supabase_db import (
    get_user, update_wallet, deduct_wallet, get_all_users, create_transaction, get_stock_counts
)
from utils.log_utils import send_log
from utils.text_utils import toSmallCaps
import json
import os
from datetime import datetime


def register_admin(dp):
    """Register all admin commands and handlers"""
    
    # Helper function to check admin
    def is_admin(user_id):
        return user_id in ADMINS
    
    # ========== MAIN ADMIN PANEL ==========
    @dp.message_handler(commands=["admin"])
    async def admin_panel(message: types.Message):
        if not is_admin(message.from_user.id):
            await message.answer(toSmallCaps("<b>🚫 You Are Not Authorized To Use Admin Commands.</b>"), parse_mode="HTML")
            return

        kb = InlineKeyboardMarkup(row_width=2)
        kb.add(
            InlineKeyboardButton(toSmallCaps("👥 Users"), callback_data="admin_users"),
            InlineKeyboardButton(toSmallCaps("💳 Payments"), callback_data="admin_payments"),
            InlineKeyboardButton(toSmallCaps("📦 Subscriptions"), callback_data="admin_subs"),
            InlineKeyboardButton(toSmallCaps("💰 Wallet"), callback_data="admin_wallet"),
            InlineKeyboardButton(toSmallCaps("🎁 Referrals"), callback_data="admin_referrals"),
            InlineKeyboardButton(toSmallCaps("📢 Broadcast"), callback_data="admin_broadcast"),
            InlineKeyboardButton(toSmallCaps("📊 Analytics"), callback_data="admin_analytics"),
            InlineKeyboardButton(toSmallCaps("📦 Stocks"), callback_data="admin_stocks"),
            InlineKeyboardButton(toSmallCaps("⚙️ Bot Settings"), callback_data="admin_settings"),
        )
        
        text = toSmallCaps(
            "<b>🧑‍💻 ADMIN PANEL\n"
            "━━━━━━━━━━━━━━\n\n"
            "Select A Section Below:</b>"
        )
        
        await message.answer(text, parse_mode="HTML", reply_markup=kb)

    # ========== USERS MANAGEMENT ==========
    @dp.message_handler(commands=["users"])
    async def cmd_users(message: types.Message):
        if not is_admin(message.from_user.id):
            return
        
        users_data = get_all_users()
        total = len(users_data)
        
        await message.answer(
            toSmallCaps(f"<b>👥 Total Users: {total}</b>"),
            parse_mode="HTML"
        )
    
    @dp.message_handler(commands=["user"])
    async def cmd_user(message: types.Message):
        if not is_admin(message.from_user.id):
            return
        
        args = message.get_args()
        if not args:
            await message.answer(toSmallCaps("<b>Usage: /user USER_ID</b>"), parse_mode="HTML")
            return
        
        try:
            user_id = int(args)
            user = get_user(user_id)
            
            if not user:
                await message.answer(toSmallCaps("<b>❌ User Not Found</b>"), parse_mode="HTML")
                return
            
            subs_count = len(user.get("subscriptions", []))
            refs_count = len(user.get("referrals", []))
            
            text = toSmallCaps(
                f"<b>👤 USER PROFILE\n"
                f"━━━━━━━━━━━━━━\n"
                f"🆔 ID: {user_id}\n"
                f"👤 Name: {user.get('name', 'N/A')}\n"
                f"💰 Wallet: ₹{user.get('wallet', 0)}\n"
                f"📦 Subscriptions: {subs_count}\n"
                f"🎁 Referrals: {refs_count}\n"
                f"📅 Joined: {user.get('joined_at', 'N/A')[:10]}</b>"
            )
            
            await message.answer(text, parse_mode="HTML")
        except:
            await message.answer(toSmallCaps("<b>❌ Invalid User ID</b>"), parse_mode="HTML")
    
    @dp.message_handler(commands=["setbalance"])
    async def cmd_setbalance(message: types.Message):
        if not is_admin(message.from_user.id):
            return
        
        args = message.get_args().split()
        if len(args) != 2:
            await message.answer(toSmallCaps("<b>Usage: /setbalance USER_ID AMOUNT</b>"), parse_mode="HTML")
            return
        
        try:
            user_id = int(args[0])
            amount = int(args[1])
            new_balance = update_wallet(user_id, amount)
            
            await message.answer(
                toSmallCaps(f"<b>✅ Added ₹{amount} To User {user_id}\n💰 New Balance: ₹{new_balance}</b>"),
                parse_mode="HTML"
            )
            await send_log(f"💰 *Admin Added Balance*\nUser: `{user_id}`\nAmount: ₹{amount}")
        except Exception as e:
            await message.answer(toSmallCaps(f"<b>❌ Error: {e}</b>"), parse_mode="HTML")
    
    @dp.message_handler(commands=["resetwallet"])
    async def cmd_resetwallet(message: types.Message):
        if not is_admin(message.from_user.id):
            return
        
        args = message.get_args()
        if not args:
            await message.answer(toSmallCaps("<b>Usage: /resetwallet USER_ID</b>"), parse_mode="HTML")
            return
        
        try:
            user_id = int(args)
            user_data = get_user(user_id)
            if user_data:
                user_data["wallet"] = 0
                save_user_data(user_id, user_data)
                await message.answer(toSmallCaps(f"<b>✅ Wallet Reset For User {user_id}</b>"), parse_mode="HTML")
        except:
            await message.answer(toSmallCaps("<b>❌ Error</b>"), parse_mode="HTML")

    # ========== PAYMENTS MANAGEMENT ==========
    @dp.message_handler(commands=["payments"])
    async def cmd_payments(message: types.Message):
        if not is_admin(message.from_user.id):
            return
        
        transactions = _read_transactions()
        recent = list(transactions.values())[-10:]
        
        if not recent:
            await message.answer(toSmallCaps("<b>📊 No Transactions Found</b>"), parse_mode="HTML")
            return
        
        text = toSmallCaps("<b>💳 RECENT TRANSACTIONS\n━━━━━━━━━━━━━━\n\n</b>")
        for txn in reversed(recent):
            text += f"• User: {txn.get('user_id')} | ₹{txn.get('amount')} | {txn.get('description')}\n"
        
        await message.answer(text, parse_mode="HTML")

    # ========== WALLET SYSTEM ==========
    @dp.message_handler(commands=["wallets"])
    async def cmd_wallets(message: types.Message):
        if not is_admin(message.from_user.id):
            return
        
        users_data = get_all_users()
        total_balance = sum(user.get("wallet", 0) for user in users_data)
        
        await message.answer(
            toSmallCaps(f"<b>💰 Total Wallet Balance: ₹{total_balance}</b>"),
            parse_mode="HTML"
        )
    
    @dp.message_handler(commands=["addfunds"])
    async def cmd_addfunds(message: types.Message):
        if not is_admin(message.from_user.id):
            return
        
        args = message.get_args().split()
        if len(args) != 2:
            await message.answer(toSmallCaps("<b>Usage: /addfunds USER_ID AMOUNT</b>"), parse_mode="HTML")
            return
        
        try:
            user_id = int(args[0])
            amount = int(args[1])
            new_balance = update_wallet(user_id, amount)
            
            await message.answer(
                toSmallCaps(f"<b>✅ Added ₹{amount}\n💰 New Balance: ₹{new_balance}</b>"),
                parse_mode="HTML"
            )
        except Exception as e:
            await message.answer(toSmallCaps(f"<b>❌ Error: {e}</b>"), parse_mode="HTML")
    
    @dp.message_handler(commands=["deduct"])
    async def cmd_deduct(message: types.Message):
        if not is_admin(message.from_user.id):
            return
        
        args = message.get_args().split()
        if len(args) != 2:
            await message.answer(toSmallCaps("<b>Usage: /deduct USER_ID AMOUNT</b>"), parse_mode="HTML")
            return
        
        try:
            user_id = int(args[0])
            amount = int(args[1])
            success = deduct_wallet(user_id, amount)
            
            if success:
                await message.answer(toSmallCaps(f"<b>✅ Deducted ₹{amount} From User {user_id}</b>"), parse_mode="HTML")
            else:
                await message.answer(toSmallCaps("<b>❌ Insufficient Balance</b>"), parse_mode="HTML")
        except Exception as e:
            await message.answer(toSmallCaps(f"<b>❌ Error: {e}</b>"), parse_mode="HTML")

    # ========== REFERRAL SYSTEM ==========
    @dp.message_handler(commands=["referrals"])
    async def cmd_referrals(message: types.Message):
        if not is_admin(message.from_user.id):
            return
        
        users_data = _read_all()
        total_refs = sum(len(user.get("referrals", [])) for user in users_data.values())
        
        await message.answer(
            toSmallCaps(f"<b>🎁 Total Referrals: {total_refs}</b>"),
            parse_mode="HTML"
        )

    # ========== BROADCAST ==========
    @dp.message_handler(commands=["broadcast"])
    async def cmd_broadcast(message: types.Message):
        if not is_admin(message.from_user.id):
            return
        
        text = message.get_args()
        if not text:
            await message.answer(toSmallCaps("<b>Usage: /broadcast Your Message Here</b>"), parse_mode="HTML")
            return
        
        users_data = _read_all()
        success = 0
        failed = 0
        
        for user_id in users_data.keys():
            try:
                await message.bot.send_message(int(user_id), text, parse_mode="HTML")
                success += 1
            except:
                failed += 1
        
        await message.answer(
            toSmallCaps(f"<b>📢 Broadcast Complete\n✅ Sent: {success}\n❌ Failed: {failed}</b>"),
            parse_mode="HTML"
        )
        await send_log(f"📢 *Broadcast Sent*\nSuccess: {success}\nFailed: {failed}")

    # ========== ANALYTICS ==========
    @dp.message_handler(commands=["stats"])
    async def cmd_stats(message: types.Message):
        if not is_admin(message.from_user.id):
            return
        
        users_data = _read_all()
        transactions = _read_transactions()
        
        total_users = len(users_data)
        total_wallet = sum(user.get("wallet", 0) for user in users_data.values())
        total_subs = sum(len(user.get("subscriptions", [])) for user in users_data.values())
        total_refs = sum(len(user.get("referrals", [])) for user in users_data.values())
        total_txns = len(transactions)
        
        text = toSmallCaps(
            f"<b>📊 BOT STATISTICS\n"
            f"━━━━━━━━━━━━━━\n\n"
            f"👥 Total Users: {total_users}\n"
            f"💰 Total Wallet: ₹{total_wallet}\n"
            f"📦 Active Subs: {total_subs}\n"
            f"🎁 Total Referrals: {total_refs}\n"
            f"💳 Transactions: {total_txns}\n"
            f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}</b>"
        )
        
        await message.answer(text, parse_mode="HTML")
    
    @dp.message_handler(commands=["plans"])
    async def cmd_plans(message: types.Message):
        if not is_admin(message.from_user.id):
            return
        
        text = toSmallCaps("<b>📦 AVAILABLE PLANS\n━━━━━━━━━━━━━━\n\n</b>")
        for key, plan in PLANS.items():
            text += f"• {plan['name']} - ₹{plan['price']}\n"
        
        await message.answer(text, parse_mode="HTML")
    
    @dp.message_handler(commands=["editplan"])
    async def cmd_editplan(message: types.Message):
        if not is_admin(message.from_user.id):
            return
        
        args = message.get_args().split()
        if len(args) != 2:
            await message.answer(
                toSmallCaps("<b>Usage: /editplan PLAN_KEY NEW_PRICE\n\nAvailable Plans:\n• netflix_4k\n• prime_video\n• youtube\n• pornhub\n• combo</b>"),
                parse_mode="HTML"
            )
            return
        
        try:
            plan_key = args[0].lower()
            new_price = int(args[1])
            
            # Import config to check plan exists
            from config.settings import PLANS as current_plans
            
            if plan_key not in current_plans:
                await message.answer(toSmallCaps("<b>❌ Invalid Plan Key</b>"), parse_mode="HTML")
                return
            
            # Update in the file permanently
            settings_path = "config/settings.py"
            with open(settings_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find and replace the price in the file
            import re
            pattern = f'"{plan_key}":\\s*{{[^}}]*"price":\\s*\\d+'
            match = re.search(pattern, content)
            if match:
                old_section = match.group()
                new_section = re.sub(r'"price":\s*\d+', f'"price": {new_price}', old_section)
                content = content.replace(old_section, new_section)
                
                with open(settings_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            await message.answer(
                toSmallCaps(f"<b>✅ Plan Updated!\n\n{current_plans[plan_key]['name']}\nNew Price: ₹{new_price}\n\n⚠️ Restart Bot To Apply Changes</b>"),
                parse_mode="HTML"
            )
            await send_log(f"📦 *Plan Price Updated*\nPlan: {plan_key}\nNew Price: ₹{new_price}\n\n⚠️ Use /restart to apply")
        except Exception as e:
            await message.answer(toSmallCaps(f"<b>❌ Error: {e}</b>"), parse_mode="HTML")

    # ========== CALLBACK HANDLERS ==========
    @dp.callback_query_handler(lambda c: c.data.startswith("admin_"))
    async def admin_callbacks(callback: types.CallbackQuery):
        if not is_admin(callback.from_user.id):
            await callback.answer("🚫 Unauthorized", show_alert=True)
            return
        
        action = callback.data.split("_")[1]
        
        if action == "users":
            users_data = get_all_users()
            text = toSmallCaps(f"<b>👥 USER MANAGEMENT\n━━━━━━━━━━━━━━\n\nTotal Users: {len(users_data)}\n\nCommands:\n/users - Total count\n/user ID - View profile\n/setbalance ID AMOUNT\n/resetwallet ID</b>")
            await callback.message.edit_text(text, parse_mode="HTML")
        
        elif action == "payments":
            text = toSmallCaps("<b>💳 PAYMENT MANAGEMENT\n━━━━━━━━━━━━━━\n\nCommands:\n/payments - Recent\n/wallets - Total balance</b>")
            await callback.message.edit_text(text, parse_mode="HTML")
        
        elif action == "wallet":
            text = toSmallCaps("<b>💰 WALLET SYSTEM\n━━━━━━━━━━━━━━\n\nCommands:\n/wallets - Total\n/addfunds ID AMOUNT\n/deduct ID AMOUNT</b>")
            await callback.message.edit_text(text, parse_mode="HTML")
        
        elif action == "referrals":
            text = toSmallCaps("<b>🎁 REFERRAL SYSTEM\n━━━━━━━━━━━━━━\n\nCommands:\n/referrals - Stats</b>")
            await callback.message.edit_text(text, parse_mode="HTML")
        
        elif action == "broadcast":
            text = toSmallCaps("<b>📢 BROADCAST\n━━━━━━━━━━━━━━\n\nCommands:\n/broadcast MESSAGE</b>")
            await callback.message.edit_text(text, parse_mode="HTML")
        
        elif action == "analytics":
            text = toSmallCaps("<b>📊 ANALYTICS\n━━━━━━━━━━━━━━\n\nCommands:\n/stats - Overview\n/plans - All plans</b>")
            await callback.message.edit_text(text, parse_mode="HTML")
        
        elif action == "stocks":
            # Get real-time stock counts for all platforms
            stock_counts = get_stock_counts()
            
            text = toSmallCaps("<b>📦 REAL-TIME STOCK INVENTORY\n━━━━━━━━━━━━━━\n\n</b>")
            
            platform_names = {
                "netflix_4k": "📺 Netflix 4K",
                "prime_video": "🎬 Prime Video",
                "youtube": "🎵 YouTube Premium",
                "pornhub": "🔞 Pornhub",
                "combo": "🎁 Combo Plan",
                "spotify": "🎶 Spotify",
                "sonyliv": "📱 Sony LIV",
                "zee5": "📱 Zee5"
            }
            
            for plan_key, counts in stock_counts.items():
                platform_name = platform_names.get(plan_key, plan_key.upper())
                total = counts["total"]
                unused = counts["unused"]
                used = counts["used"]
                
                # Status emoji based on stock
                if unused == 0:
                    status = "❌"
                elif unused < 5:
                    status = "⚠️"
                else:
                    status = "✅"
                
                text += (
                    f"{status} {toSmallCaps(platform_name)}\n"
                    f"   {toSmallCaps('Available')}: {unused} | "
                    f"{toSmallCaps('Used')}: {used} | "
                    f"{toSmallCaps('Total')}: {total}\n\n"
                )
            
            text += toSmallCaps("\n✅ = Good Stock (5+)\n⚠️ = Low Stock (&lt;5)\n❌ = Out of Stock")
            
            await callback.message.edit_text(text, parse_mode="HTML")
        
        elif action == "subs":
            # Redirect to advanced subscription panel
            kb = InlineKeyboardMarkup(row_width=2)
            kb.add(
                InlineKeyboardButton(toSmallCaps("🎵 YouTube"), callback_data="admin_ott_youtube"),
                InlineKeyboardButton(toSmallCaps("🎬 Prime Video"), callback_data="admin_ott_prime_video"),
                InlineKeyboardButton(toSmallCaps("📺 Netflix"), callback_data="admin_ott_netflix_4k"),
                InlineKeyboardButton(toSmallCaps("📦 Combo"), callback_data="admin_ott_combo"),
                InlineKeyboardButton(toSmallCaps("🔞 Pornhub"), callback_data="admin_ott_pornhub"),
            )
            kb.add(InlineKeyboardButton(toSmallCaps("🔙 Back to Admin"), callback_data="admin_back"))
            
            text = toSmallCaps(
                "<b>📦 SUBSCRIPTION MANAGEMENT\n"
                "━━━━━━━━━━━━━━\n\n"
                "Select OTT Platform To Manage:</b>"
            )
            
            await callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
        
        elif action == "settings":
            text = toSmallCaps("<b>⚙️ BOT SETTINGS\n━━━━━━━━━━━━━━\n\nComing Soon...</b>")
            await callback.message.edit_text(text, parse_mode="HTML")
        
        await callback.answer()
