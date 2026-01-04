"""
Advanced Admin Subscription Management Panel
Button-based, no slash commands
"""
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from config.settings import ADMINS
from utils.supabase_db import (
    get_all_plans, get_plan, update_plan_price, toggle_plan_active, 
    add_stock, get_stock_count, add_credentials, update_plan_details
)
from utils.log_utils import send_log
from utils.text_utils import toSmallCaps


class AdminStockStates(StatesGroup):
    waiting_for_credentials = State()
    waiting_for_price = State()
    waiting_for_description = State()


def register_admin_subs(dp):
    """Register admin subscription management handlers"""
    
    def is_admin(user_id):
        return user_id in ADMINS
    
    # ========== MAIN SUBSCRIPTIONS PANEL ==========
    @dp.callback_query_handler(lambda c: c.data == "admin_subs_main", state="*")
    async def admin_subs_main(callback: types.CallbackQuery, state: FSMContext):
        await state.finish()
        
        if not is_admin(callback.from_user.id):
            await callback.answer("🚫 Unauthorized", show_alert=True)
            return
        
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
        await callback.answer()
    
    # ========== OTT PLAN DETAILS ==========
    @dp.callback_query_handler(lambda c: c.data.startswith("admin_ott_"), state="*")
    async def show_ott_details(callback: types.CallbackQuery, state: FSMContext):
        await state.finish()
        
        print(f"🔍 DEBUG: Callback data = {callback.data}")
        print(f"🔍 DEBUG: User ID = {callback.from_user.id}")
        
        if not is_admin(callback.from_user.id):
            await callback.answer("🚫 Unauthorized", show_alert=True)
            return
        
        plan_key = callback.data.replace("admin_ott_", "")
        print(f"🔍 DEBUG: Plan key = {plan_key}")
        
        plan = get_plan(plan_key)
        print(f"🔍 DEBUG: Plan = {plan}")
        
        if not plan:
            await callback.answer("❌ Plan not found", show_alert=True)
            return
        
        stock = get_stock_count(plan_key)
        status = "✅ Active" if plan.get("active", True) else "❌ Disabled"
        
        text = toSmallCaps(
            f"<b>📦 {plan['ott_name']}\n"
            f"━━━━━━━━━━━━━━\n\n"
            f"💳 Price: ₹{plan['price']}\n"
            f"📊 Stock: {stock}\n"
            f"🔘 Status: {status}\n\n"
            f"📝 Details:\n{plan.get('description', 'No description')}</b>"
        )
        
        kb = InlineKeyboardMarkup(row_width=2)
        kb.add(
            InlineKeyboardButton(toSmallCaps("✏️ Edit Price"), callback_data=f"edit_price_{plan_key}"),
            InlineKeyboardButton(toSmallCaps("📝 Edit Details"), callback_data=f"edit_desc_{plan_key}"),
        )
        kb.add(
            InlineKeyboardButton(toSmallCaps("➕ Add Stock"), callback_data=f"add_stock_{plan_key}"),
            InlineKeyboardButton(toSmallCaps("📋 View Stock"), callback_data=f"view_stock_{plan_key}"),
        )
        
        toggle_text = "❌ Disable Plan" if plan.get("active", True) else "✅ Enable Plan"
        kb.add(InlineKeyboardButton(toSmallCaps(toggle_text), callback_data=f"toggle_{plan_key}"))
        kb.add(InlineKeyboardButton(toSmallCaps("🔙 Back"), callback_data="admin_subs_main"))
        
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
        await callback.answer()
    
    # ========== EDIT PRICE ==========
    @dp.callback_query_handler(lambda c: c.data.startswith("edit_price_"), state="*")
    async def edit_price_start(callback: types.CallbackQuery, state: FSMContext):
        if not is_admin(callback.from_user.id):
            await callback.answer("🚫 Unauthorized", show_alert=True)
            return
        
        plan_key = callback.data.replace("edit_price_", "")
        await state.update_data(plan_key=plan_key, action="price")
        await AdminStockStates.waiting_for_price.set()
        
        await callback.message.edit_text(
            toSmallCaps("<b>✏️ Enter New Price\n\nExample: 99 or 149\n\nSend /cancel to abort</b>"),
            parse_mode="HTML"
        )
        await callback.answer()
    
    @dp.message_handler(state=AdminStockStates.waiting_for_price)
    async def edit_price_finish(message: types.Message, state: FSMContext):
        if not is_admin(message.from_user.id):
            return
        
        if message.text == "/cancel":
            await state.finish()
            await message.answer(toSmallCaps("<b>❌ Cancelled</b>"), parse_mode="HTML")
            return
        
        try:
            new_price = int(message.text)
            data = await state.get_data()
            plan_key = data.get("plan_key")
            
            update_plan_price(plan_key, new_price)
            plan = get_plan(plan_key)
            
            await message.answer(
                toSmallCaps(f"<b>✅ Price Updated!\n\n{plan['ott_name']}\nNew Price: ₹{new_price}</b>"),
                parse_mode="HTML"
            )
            
            await send_log(f"💰 *Price Updated*\nPlan: {plan['ott_name']}\nNew Price: ₹{new_price}\nBy: {message.from_user.id}")
            await state.finish()
            
        except ValueError:
            await message.answer(toSmallCaps("<b>❌ Invalid price! Send a number.</b>"), parse_mode="HTML")
    
    # ========== EDIT DESCRIPTION ==========
    @dp.callback_query_handler(lambda c: c.data.startswith("edit_desc_"), state="*")
    async def edit_desc_start(callback: types.CallbackQuery, state: FSMContext):
        if not is_admin(callback.from_user.id):
            await callback.answer("🚫 Unauthorized", show_alert=True)
            return
        
        plan_key = callback.data.replace("edit_desc_", "")
        await state.update_data(plan_key=plan_key)
        await AdminStockStates.waiting_for_description.set()
        
        await callback.message.edit_text(
            toSmallCaps("<b>📝 Enter New Description\n\nExample:\nPrivate Single Screen | Full HD | 1 Month\n\nSend /cancel to abort</b>"),
            parse_mode="HTML"
        )
        await callback.answer()
    
    @dp.message_handler(state=AdminStockStates.waiting_for_description)
    async def edit_desc_finish(message: types.Message, state: FSMContext):
        if not is_admin(message.from_user.id):
            return
        
        if message.text == "/cancel":
            await state.finish()
            await message.answer(toSmallCaps("<b>❌ Cancelled</b>"), parse_mode="HTML")
            return
        
        data = await state.get_data()
        plan_key = data.get("plan_key")
        
        update_plan_details(plan_key, message.text)
        plan = get_plan(plan_key)
        
        await message.answer(
            toSmallCaps(f"<b>✅ Description Updated!\n\n{plan['ott_name']}</b>"),
            parse_mode="HTML"
        )
        
        await send_log(f"📝 *Description Updated*\nPlan: {plan['ott_name']}\nBy: {message.from_user.id}")
        await state.finish()
    
    # ========== ADD STOCK ==========
    @dp.callback_query_handler(lambda c: c.data.startswith("add_stock_"), state="*")
    async def add_stock_start(callback: types.CallbackQuery, state: FSMContext):
        if not is_admin(callback.from_user.id):
            await callback.answer("🚫 Unauthorized", show_alert=True)
            return
        
        plan_key = callback.data.replace("add_stock_", "")
        await state.update_data(plan_key=plan_key)
        await AdminStockStates.waiting_for_credentials.set()
        
        text = toSmallCaps(
            "<b>➕ ADD STOCK\n"
            "━━━━━━━━━━━━━━\n\n"
            "Send credentials in this format:\n"
            "email:password\n\n"
            "For bulk upload, send multiple lines:\n"
            "email1:pass1\n"
            "email2:pass2\n"
            "email3:pass3\n\n"
            "Send /cancel to abort</b>"
        )
        
        await callback.message.edit_text(text, parse_mode="HTML")
        await callback.answer()
    
    @dp.message_handler(state=AdminStockStates.waiting_for_credentials)
    async def add_stock_finish(message: types.Message, state: FSMContext):
        if not is_admin(message.from_user.id):
            return
        
        if message.text == "/cancel":
            await state.finish()
            await message.answer(toSmallCaps("<b>❌ Cancelled</b>"), parse_mode="HTML")
            return
        
        # Parse credentials
        lines = message.text.strip().split("\n")
        credentials_list = []
        invalid = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if ":" not in line:
                invalid.append(line)
                continue
            
            credentials_list.append(line)
        
        if not credentials_list:
            await message.answer(
                toSmallCaps("<b>❌ No valid credentials found!\n\nFormat: email:password</b>"),
                parse_mode="HTML"
            )
            return
        
        # Add to database
        data = await state.get_data()
        plan_key = data.get("plan_key")
        
        result = add_credentials(plan_key, credentials_list)
        plan = get_plan(plan_key)
        
        text = toSmallCaps(
            f"<b>✅ Stock Added Successfully!\n\n"
            f"📦 Plan: {plan['ott_name']}\n"
            f"➕ Added: {result['added']}\n"
            f"❌ Duplicates: {result['duplicates']}\n"
            f"📊 Total Stock: {result['total']}\n\n"
            f"{'⚠️ ' + str(len(invalid)) + ' invalid lines skipped' if invalid else ''}</b>"
        )
        
        await message.answer(text, parse_mode="HTML")
        await send_log(
            f"📦 *Stock Added*\n"
            f"Plan: {plan['ott_name']}\n"
            f"Added: {result['added']}\n"
            f"By: {message.from_user.id}"
        )
        await state.finish()
    
    # ========== VIEW STOCK ==========
    @dp.callback_query_handler(lambda c: c.data.startswith("view_stock_"), state="*")
    async def view_stock(callback: types.CallbackQuery, state: FSMContext):
        await state.finish()
        
        if not is_admin(callback.from_user.id):
            await callback.answer("🚫 Unauthorized", show_alert=True)
            return
        
        plan_key = callback.data.replace("view_stock_", "")
        plan = get_plan(plan_key)
        stocks = get_all_stock_for_plan(plan_key)
        
        unused = len([s for s in stocks if not s.get("used", False)])
        used = len([s for s in stocks if s.get("used", False)])
        
        text = toSmallCaps(
            f"<b>📋 STOCK DETAILS\n"
            f"━━━━━━━━━━━━━━\n\n"
            f"📦 Plan: {plan['ott_name']}\n"
            f"✅ Available: {unused}\n"
            f"❌ Used: {used}\n"
            f"📊 Total: {len(stocks)}</b>"
        )
        
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton(toSmallCaps("🔙 Back"), callback_data=f"admin_ott_{plan_key}"))
        
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
        await callback.answer()
    
    # ========== TOGGLE PLAN STATUS ==========
    @dp.callback_query_handler(lambda c: c.data.startswith("toggle_"), state="*")
    async def toggle_plan(callback: types.CallbackQuery, state: FSMContext):
        await state.finish()
        
        if not is_admin(callback.from_user.id):
            await callback.answer("🚫 Unauthorized", show_alert=True)
            return
        
        plan_key = callback.data.replace("toggle_", "")
        new_status = toggle_plan_active(plan_key)
        plan = get_plan(plan_key)
        
        status_text = "Enabled" if new_status else "Disabled"
        await callback.answer(f"✅ {status_text}", show_alert=True)
        
        await send_log(f"🔘 *Plan {status_text}*\nPlan: {plan['ott_name']}\nBy: {callback.from_user.id}")
        
        # Refresh the display
        await show_ott_details(callback, state)
    
    # ========== BACK TO ADMIN ==========
    @dp.callback_query_handler(lambda c: c.data == "admin_back", state="*")
    async def admin_back(callback: types.CallbackQuery, state: FSMContext):
        await state.finish()
        
        # Import here to avoid circular dependency
        from handlers.admin_handler import admin_panel
        message = callback.message
        message.from_user = callback.from_user
        await admin_panel(message)
