# ================================
# ⚙️ BOT CONFIGURATION
# ================================

BOT_TOKEN = "7412404145:AAEmu1uum9loSCU1ytqA0UmR-7yUOp-QgjI"
ADMINS = [7127370646]


# ================================
# 📁 DATA FILE PATHS
# ================================
DATA_FILE = "data/users.json"


# ================================
# 🎬 OTT PLANS CONFIG
# ================================
PLANS = {
    "netflix_4k": {
        "name": "Netflix 4K (Single Device)",
        "price": 99,
        "duration_days": 30,
        "image": "images/netflix.jpg"
    },
    "prime_video": {
        "name": "Amazon Prime Video",
        "price": 45,
        "duration_days": 30,
        "image": "images/prime.jpg"
    },
    "youtube": {
        "name": "YouTube Premium + Music",
        "price": 15,
        "duration_days": 30,
        "image": "images/youtube.jpg"
    },
    "pornhub": {
        "name": "Pornhub Premium",
        "price": 69,
        "duration_days": 30,
        "image": "images/pornhub.jpg"
    },
    "combo": {
        "name": "OTT Combo Pack",
        "price": 135,
        "duration_days": 30,
        "image": "images/combo.jpg"
    }
}


# ================================
# 🔗 REFERRAL SYSTEM
# ================================
REFERRAL_BASE_URL = "https://t.me/ottsonly1bot?start="


# ================================
# 💳 PAYMENT GATEWAY CONFIGURATION
# ================================
# UPI Payment Gateway (Paytm Merchant)
UPI_ID = "paytm.s20gimo@pty"
MERCHANT_ID = "ArjzPn65175653753590"
PAY_VERIFY_API = "https://pay-rho-seven.vercel.app/"

# Old Razorpay (backup)
RAZORPAY_KEY_ID = "rzp_live_RcvHwiXjGwjLDV"
RAZORPAY_KEY_SECRET = "nybte012bd16N7NXJBqDwDvf"
RAZORPAY_API_BASE = "https://api.razorpay.com/v1"
PAYMENT_CHECK_INTERVAL = 15  # seconds


# ================================
# 📢 LOGGING CHANNEL
# ================================
LOG_CHANNEL_ID = -1003310219165  # ✅ Updated after group migration to supergroup
