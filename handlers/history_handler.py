"""
User History Handler
Displays transaction history, purchase history, and delivered credentials
"""
from aiogram import types
from utils.supabase_db import get_user_history
from utils.text_utils import toSmallCaps
from datetime import datetime


def register_history(dp):
    """Register history command handler"""
    
    @dp.message_handler(commands=["history"])
    async def cmd_history(message: types.Message):
        """
        Show user's complete history:
        - Transactions
        - Purchases
        - Delivered credentials
        """
        telegram_id = message.from_user.id
        
        # Fetch user history
        history = get_user_history(telegram_id)
        
        # Build the response message
        response_parts = [toSmallCaps("<b>📜 YOUR ACCOUNT HISTORY</b>\n")]
        
        # ========== TRANSACTION HISTORY ==========
        transactions = history.get("transactions", [])
        response_parts.append(toSmallCaps("\n<b>💳 TRANSACTION HISTORY</b>"))
        
        if transactions:
            for txn in transactions[:10]:  # Show last 10 transactions
                amount = txn.get("amount", 0)
                txn_type = txn.get("transaction_type", "unknown")
                description = txn.get("description", "Transaction")
                created_at = txn.get("created_at", "")
                
                # Format date
                try:
                    date_obj = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                    date_str = date_obj.strftime("%d %b %Y")
                except:
                    date_str = "Unknown date"
                
                # Format amount with sign
                if amount > 0:
                    amount_str = f"+₹{amount}"
                    type_emoji = "💰"
                else:
                    amount_str = f"−₹{abs(amount)}"
                    type_emoji = "💸"
                
                response_parts.append(
                    toSmallCaps(f"• {type_emoji} {amount_str} | {description} | {date_str}")
                )
        else:
            response_parts.append(toSmallCaps("• No transactions yet"))
        
        # ========== PURCHASE HISTORY ==========
        purchases = history.get("purchases", [])
        response_parts.append(toSmallCaps("\n\n<b>🛒 PURCHASE HISTORY</b>"))
        
        if purchases:
            for purchase in purchases[:10]:  # Show last 10 purchases
                plan_data = purchase.get("plans", {})
                plan_name = plan_data.get("ott_name", "Unknown Plan")
                plan_price = plan_data.get("price", 0)
                created_at = purchase.get("created_at", "")
                
                # Format date
                try:
                    date_obj = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                    date_str = date_obj.strftime("%d %b %Y")
                except:
                    date_str = "Unknown date"
                
                response_parts.append(
                    toSmallCaps(
                        f"• {plan_name} — ₹{plan_price}\n"
                        f"  📅 Purchased: {date_str}\n"
                        f"  ✅ Status: Active"
                    )
                )
        else:
            response_parts.append(toSmallCaps("• No purchases yet"))
        
        # ========== DELIVERED CREDENTIALS ==========
        credentials = history.get("credentials", [])
        response_parts.append(toSmallCaps("\n\n<b>🔐 YOUR CREDENTIALS</b>"))
        
        if credentials:
            for cred in credentials[:10]:  # Show last 10 credentials
                plan_data = cred.get("plans", {})
                plan_name = plan_data.get("ott_name", "Unknown Plan")
                credential_str = cred.get("credential", "N/A")
                used_at = cred.get("used_at", "")
                
                # Format date
                try:
                    date_obj = datetime.fromisoformat(used_at.replace("Z", "+00:00"))
                    date_str = date_obj.strftime("%d %b %Y")
                except:
                    date_str = "Unknown date"
                
                # Parse credentials (format: email:password)
                if ":" in credential_str:
                    parts = credential_str.split(":", 1)
                    email = parts[0].strip()
                    password = parts[1].strip()
                else:
                    email = credential_str
                    password = "N/A"
                
                response_parts.append(
                    toSmallCaps(f"• {plan_name}") + "\n" +
                    f"  {toSmallCaps('📧 ID')}: <code>{email}</code>\n" +
                    f"  {toSmallCaps('🔑 Password')}: <code>{password}</code>\n" +
                    toSmallCaps(f"  📅 Delivered: {date_str}")
                )
        else:
            response_parts.append(toSmallCaps("• No credentials delivered yet"))
        
        # Join all parts and send
        response_text = "\n".join(response_parts)
        
        await message.answer(response_text, parse_mode="HTML")
