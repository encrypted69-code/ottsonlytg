"""
Example integration with Telegram Bot
Complete examples for all common operations
"""
import requests
from typing import Optional

# Configuration
API_BASE_URL = "http://localhost:8000"


class ReferralSystemAPI:
    """Simple API client for referral system"""
    
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
    
    # ==================== USER OPERATIONS ====================
    
    def register_user(
        self,
        telegram_id: int,
        username: Optional[str],
        first_name: Optional[str],
        last_name: Optional[str] = None,
        referral_code: Optional[str] = None
    ):
        """Register new user in referral system"""
        response = requests.post(
            f"{self.base_url}/users/create",
            json={
                "telegram_id": telegram_id,
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
                "referred_by_code": referral_code
            }
        )
        return response.json()
    
    def get_user(self, telegram_id: int):
        """Get user details"""
        response = requests.get(f"{self.base_url}/users/{telegram_id}")
        return response.json()
    
    def get_referral_stats(self, telegram_id: int):
        """Get user's referral statistics"""
        response = requests.get(f"{self.base_url}/users/{telegram_id}/referral-stats")
        return response.json()
    
    def get_referral_tree(self, telegram_id: int):
        """Get complete referral tree"""
        response = requests.get(f"{self.base_url}/users/{telegram_id}/referral-tree")
        return response.json()
    
    # ==================== ORDER OPERATIONS ====================
    
    def create_order(
        self,
        user_id: int,
        payment_method: str = "upi",
        upi_id: Optional[str] = None
    ):
        """Create new order"""
        response = requests.post(
            f"{self.base_url}/orders/create",
            json={
                "user_id": user_id,
                "payment_method": payment_method,
                "upi_id": upi_id
            }
        )
        return response.json()
    
    def process_payment_success(
        self,
        order_id: str,
        transaction_id: Optional[str] = None
    ):
        """Mark payment as successful"""
        response = requests.post(
            f"{self.base_url}/orders/{order_id}/payment-success",
            json={"transaction_id": transaction_id}
        )
        return response.json()
    
    def get_order(self, order_id: str):
        """Get order details"""
        response = requests.get(f"{self.base_url}/orders/{order_id}")
        return response.json()
    
    # ==================== WALLET OPERATIONS ====================
    
    def get_wallet(self, user_id: int):
        """Get user wallet balance"""
        response = requests.get(f"{self.base_url}/wallet/{user_id}")
        return response.json()
    
    def get_wallet_transactions(self, user_id: int, limit: int = 50):
        """Get wallet transaction history"""
        response = requests.get(
            f"{self.base_url}/wallet/{user_id}/transactions",
            params={"limit": limit}
        )
        return response.json()
    
    # ==================== WITHDRAWAL OPERATIONS ====================
    
    def create_withdrawal(
        self,
        user_token: str,
        amount: float,
        upi_id: str
    ):
        """Create withdrawal request"""
        headers = {"Authorization": f"Bearer {user_token}"}
        response = requests.post(
            f"{self.base_url}/withdrawals/create",
            headers=headers,
            json={
                "amount": amount,
                "withdrawal_method": "upi",
                "upi_id": upi_id
            }
        )
        return response.json()


# ==================== TELEGRAM BOT EXAMPLES ====================

# Initialize API client
api = ReferralSystemAPI()


def handle_start_command(telegram_id: int, username: str, first_name: str, referral_code: Optional[str] = None):
    """
    Example: /start command handler
    Creates user in referral system and returns their referral link
    """
    # Register user
    user = api.register_user(
        telegram_id=telegram_id,
        username=username,
        first_name=first_name,
        referral_code=referral_code
    )
    
    # Generate referral link
    bot_username = "YourBotUsername"
    referral_link = f"https://t.me/{bot_username}?start=ref_{user['referral_code']}"
    
    return f"""
🎉 Welcome {first_name}!

Your account is ready.

💰 Start earning by sharing your referral link:
{referral_link}

Earn ₹28 for every Level 1 referral
Earn ₹9 for every Level 2 referral
    """


def handle_buy_command(telegram_id: int):
    """
    Example: /buy command handler
    Creates order and shows payment details
    """
    # Create order
    order = api.create_order(
        user_id=telegram_id,
        payment_method="upi"
    )
    
    return f"""
📦 Order Created!

Order ID: {order['order_id']}
Amount: ₹{order['selling_price']}

Please complete the payment using UPI.
After payment, send transaction ID.
    """


def handle_payment_callback(order_id: str, transaction_id: str, upi_id: str):
    """
    Example: Payment gateway callback handler
    Processes successful payment
    """
    # Mark payment as successful
    order = api.process_payment_success(
        order_id=order_id,
        transaction_id=transaction_id
    )
    
    # This automatically:
    # - Credits commission to referrers (pending for 24h)
    # - Updates user stats
    # - Marks referral as converted
    # - Runs fraud checks
    
    return f"""
✅ Payment Successful!

Order: {order_id}
Transaction: {transaction_id}

Your subscription is now active!
    """


def handle_wallet_command(telegram_id: int):
    """
    Example: /wallet command handler
    Shows user's wallet balance
    """
    wallet = api.get_wallet(telegram_id)
    
    return f"""
💰 Your Wallet

Total Balance: ₹{wallet['total_balance']}
Withdrawable: ₹{wallet['withdrawable_balance']}
Pending (24h hold): ₹{wallet['pending_balance']}

Total Earned: ₹{wallet['total_earned']}
Total Withdrawn: ₹{wallet['total_withdrawn']}

Use /withdraw to request withdrawal (minimum ₹500)
    """


def handle_stats_command(telegram_id: int):
    """
    Example: /stats command handler
    Shows referral statistics
    """
    stats = api.get_referral_stats(telegram_id)
    
    return f"""
📊 Your Referral Stats

Total Clicks: {stats['total_clicks']}
Total Referrals: {stats['total_referrals']}
  └─ Level 1: {stats['level1_referrals']}
  └─ Level 2: {stats['level2_referrals']}

Buyers: {stats['total_buyers']}
Conversion Rate: {stats['conversion_rate']}%

💰 Commission Earned: ₹{stats['total_commission_earned']}
💸 Commission Paid: ₹{stats['total_commission_paid']}
⏳ Pending Commission: ₹{stats['pending_commission']}
    """


def handle_withdraw_command(telegram_id: int, amount: float, upi_id: str, user_token: str):
    """
    Example: /withdraw command handler
    Creates withdrawal request
    """
    try:
        withdrawal = api.create_withdrawal(
            user_token=user_token,
            amount=amount,
            upi_id=upi_id
        )
        
        return f"""
✅ Withdrawal Request Created

Withdrawal ID: {withdrawal['withdrawal_id']}
Amount: ₹{withdrawal['amount']}
UPI ID: {withdrawal['upi_id']}

Status: Pending Admin Approval

You'll be notified once approved and paid.
        """
    except Exception as e:
        return f"❌ Error: {str(e)}"


def handle_referrals_command(telegram_id: int):
    """
    Example: /referrals command handler
    Shows referral tree
    """
    tree = api.get_referral_tree(telegram_id)
    
    level1_count = len(tree['level1'])
    level2_count = len(tree['level2'])
    
    # Format level 1 referrals
    level1_text = "\n".join([
        f"  • {r['first_name']} (@{r['username']}) - {r['total_orders']} orders"
        for r in tree['level1'][:5]  # Show first 5
    ]) or "  None yet"
    
    return f"""
👥 Your Referral Network

Level 1 Referrals: {level1_count}
{level1_text}
{f'  ... and {level1_count - 5} more' if level1_count > 5 else ''}

Level 2 Referrals: {level2_count}

Total Commission: ₹{tree['stats']['total_commission_earned']}
    """


# ==================== COMPLETE BOT EXAMPLE ====================

def telegram_bot_example():
    """
    Complete example of integrating with python-telegram-bot
    """
    from telegram import Update
    from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
    
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        
        # Extract referral code from command args
        referral_code = None
        if context.args:
            referral_code = context.args[0].replace('ref_', '')
        
        # Register user
        message = handle_start_command(
            telegram_id=user.id,
            username=user.username,
            first_name=user.first_name,
            referral_code=referral_code
        )
        
        await update.message.reply_text(message)
    
    async def wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /wallet command"""
        message = handle_wallet_command(update.effective_user.id)
        await update.message.reply_text(message)
    
    async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command"""
        message = handle_stats_command(update.effective_user.id)
        await update.message.reply_text(message)
    
    async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /buy command"""
        message = handle_buy_command(update.effective_user.id)
        await update.message.reply_text(message)
    
    # Build application
    app = ApplicationBuilder().token("YOUR_BOT_TOKEN").build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("wallet", wallet))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("buy", buy))
    
    # Start bot
    app.run_polling()


# ==================== TESTING ====================

if __name__ == "__main__":
    # Test user registration
    print("Testing user registration...")
    user = api.register_user(
        telegram_id=123456789,
        username="testuser",
        first_name="Test",
        last_name="User"
    )
    print(f"User created: {user['referral_code']}")
    
    # Test order creation
    print("\nTesting order creation...")
    order = api.create_order(user_id=123456789)
    print(f"Order created: {order['order_id']}")
    
    # Test wallet retrieval
    print("\nTesting wallet retrieval...")
    wallet = api.get_wallet(123456789)
    print(f"Wallet balance: ₹{wallet['total_balance']}")
    
    print("\n✅ All tests passed!")
