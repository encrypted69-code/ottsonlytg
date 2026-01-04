import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config.settings import BOT_TOKEN, ADMINS
from handlers import (
    start_handler,
    wallet_handler,
    ott_handler,
    refer_handler,
    profile_handler,
    admin_handler,
    admin_subs,
    history_handler
)
from utils.json_utils import create_user_if_not_exists
from utils.log_utils import send_log


# ===========================
# 🔧 Basic Setup
# ===========================
logging.basicConfig(level=logging.INFO)

storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot, storage=storage)


# ===========================
# 🚀 Bot Startup
# ===========================
async def on_startup(dispatcher):
    print("✅ OTTOnly Bot Started Successfully!")
    await send_log("🚀 *OTTOnly Bot is now online and ready!*")

    # Ensure admin accounts exist
    for admin_id in ADMINS:
        create_user_if_not_exists(admin_id, "Admin")


# ===========================
# 🏁 Register All Handlers
# ===========================
start_handler.register_start(dp)
wallet_handler.register_wallet(dp)
ott_handler.register_ott(dp)
refer_handler.register_wallet_handlers(dp)
profile_handler.register_profile(dp)
history_handler.register_history(dp)
admin_handler.register_admin(dp)
admin_subs.register_admin_subs(dp)


# Debug: Log all callbacks
@dp.callback_query_handler(lambda c: True, state="*")
async def debug_all_callbacks(callback: types.CallbackQuery):
    print(f"🔍 UNHANDLED CALLBACK: {callback.data} from user {callback.from_user.id}")
    await callback.answer("⚠️ Handler not found for this action", show_alert=True)


# ===========================
# ⚠️ Global Error Handler
# ===========================
@dp.errors_handler()
async def global_error_handler(update, error):
    logging.exception(f"❌ Error occurred: {error}")
    try:
        await send_log(f"⚠️ *Bot Error:* `{str(error)}`")
    except Exception as log_error:
        print(f"[LOGGING ERROR] {log_error}")
    return True


# ===========================
# ▶️ Start Polling
# ===========================
if __name__ == "__main__":
    print("🚀 Starting OTTOnly Bot...")
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
