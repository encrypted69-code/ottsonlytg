# OTTsOnly Bot - Deployment Guide

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Git
- Supabase account
- Telegram Bot Token

### Local Setup

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd ottsonly
```

2. **Create virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your actual credentials
```

5. **Run the bot**
```bash
python main.py
```

---

## 🌐 VPS Deployment (24/7 Operation)

### Step 1: Connect to VPS
```bash
ssh username@your-vps-ip
```

### Step 2: Install Dependencies
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11+
sudo apt install python3.11 python3.11-venv python3-pip git -y
```

### Step 3: Clone and Setup
```bash
# Clone repository
git clone <your-repo-url>
cd ottsonly

# Create virtual environment
python3.11 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 4: Configure Environment
```bash
# Create .env file
nano .env
# Paste your credentials and save (Ctrl+X, Y, Enter)
```

### Step 5: Run with Screen (keeps running after logout)
```bash
# Install screen
sudo apt install screen -y

# Start a new screen session
screen -S ottbot

# Run the bot
python main.py

# Detach from screen: Press Ctrl+A then D
```

### Step 6: Manage the Bot
```bash
# Reattach to screen
screen -r ottbot

# Stop the bot: Ctrl+C inside screen

# List all screens
screen -ls

# Kill a screen session
screen -X -S ottbot quit
```

---

## 🔧 Alternative: Using systemd (Recommended for Production)

### Create systemd service
```bash
sudo nano /etc/systemd/system/ottbot.service
```

Paste this configuration:
```ini
[Unit]
Description=OTTsOnly Telegram Bot
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/home/your-username/ottsonly
Environment="PATH=/home/your-username/ottsonly/.venv/bin"
ExecStart=/home/your-username/ottsonly/.venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Enable and start service
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable ottbot

# Start service
sudo systemctl start ottbot

# Check status
sudo systemctl status ottbot

# View logs
sudo journalctl -u ottbot -f

# Restart service
sudo systemctl restart ottbot

# Stop service
sudo systemctl stop ottbot
```

---

## 📊 Database Setup (Supabase)

The bot uses Supabase PostgreSQL. Tables are:
- `users` - User accounts and wallets
- `plans` - OTT plan configurations
- `stocks` - Credential inventory
- `transactions` - Payment history
- `subscriptions` - User purchases

Tables should already exist. If not, run the migration script once locally:
```bash
python migrate_to_supabase.py
```

---

## 🔐 Security Checklist

- ✅ Never commit `.env` file to GitHub
- ✅ Never commit `.session` files
- ✅ Keep `SUPABASE_SERVICE_ROLE_KEY` secret
- ✅ Use strong passwords for VPS
- ✅ Enable UFW firewall on VPS
- ✅ Keep VPS updated regularly

---

## 🐛 Troubleshooting

### Bot not starting
```bash
# Check Python version
python --version  # Should be 3.11+

# Check if port is in use
lsof -i :8443

# Check logs
tail -f bot.log
```

### Database connection issues
- Verify Supabase URL and key in `.env`
- Check Supabase project status
- Verify internet connectivity

### Out of memory on VPS
```bash
# Check memory usage
free -h

# Consider upgrading VPS plan if < 1GB RAM
```

---

## 📝 Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `BOT_TOKEN` | Telegram bot token from @BotFather | `123456:ABCdef...` |
| `ADMIN_ID` | Your Telegram user ID | `7127370646` |
| `SUPABASE_URL` | Supabase project URL | `https://abc.supabase.co` |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service role key | `eyJ...` |
| `LOG_CHANNEL_ID` | Main logs channel ID | `-4758912978` |
| `YOUTUBE_LOG_CHANNEL_ID` | YouTube logs channel ID | `-1002780521171` |

---

## 🎯 Post-Deployment

1. Test all commands: `/start`, `/history`, `/admin`
2. Test payment flow with small amount
3. Test OTT purchases
4. Monitor logs channel
5. Set up monitoring/alerts

---

## 🔄 Updating the Bot

```bash
# Pull latest changes
git pull origin main

# Restart bot
sudo systemctl restart ottbot
# OR if using screen:
screen -r ottbot
# Ctrl+C to stop, then: python main.py
```

---

## 💡 Tips

- Use `tmux` or `screen` for manual sessions
- Use `systemd` for production (auto-restart, logging)
- Set up Cloudflare Tunnel for secure webhook (optional)
- Enable daily backups of Supabase database
- Monitor VPS resources (CPU, RAM, Disk)

---

**Ready to deploy! 🚀**
