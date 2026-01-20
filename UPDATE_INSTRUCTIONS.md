# 🚀 QUICK UPDATE GUIDE - Price Changes Applied

## ✅ Changes Made

All OTT prices have been updated:

| Plan | Old Price | New Price |
|------|-----------|-----------|
| Netflix 4K | ₹99 | **₹75** |
| Prime Video | ₹45 | **₹35** |
| YouTube Premium | ₹15 | **₹25** |
| Pornhub Premium | ₹69 | **₹60** |
| Combo Pack | ₹135 | **₹125** |

**All changes have been pushed to GitHub!** ✅

---

## 📡 Update Your VPS (3 Simple Steps)

### Step 1: Connect to Your VPS

```bash
ssh username@your-vps-ip
```

### Step 2: Navigate to Bot Directory

```bash
cd ~/ottsonly
# Or wherever your bot is installed
```

### Step 3: Run Update Script

```bash
# Make script executable (first time only)
chmod +x deploy_update.sh

# Run the update script
bash deploy_update.sh
```

**That's it!** The script will:
- ✅ Pull latest changes from GitHub
- ✅ Update dependencies if needed
- ✅ Restart the bot automatically
- ✅ Ensure it runs 24/7

---

## 📊 Verify Bot is Running

### If using **systemd** (recommended):

```bash
# Check status
sudo systemctl status ottbot

# View live logs
sudo journalctl -u ottbot -f

# If needed to restart manually
sudo systemctl restart ottbot
```

### If using **screen**:

```bash
# Check if bot is running
screen -ls

# Reattach to see live logs
screen -r ottbot

# Press Ctrl+A then D to detach (keep running)
```

### If using **background process**:

```bash
# View logs
tail -f bot.log

# Check if running
ps aux | grep main.py
```

---

## 🔒 Ensure 24/7 Operation

### Option A: Systemd (Best for VPS)

If not already set up, run this **once**:

```bash
cd ~/ottsonly
sudo bash setup_systemd.sh
```

**Benefits:**
- ✅ Auto-restart on crash
- ✅ Auto-start on server reboot
- ✅ Proper logging
- ✅ Easy management

### Option B: Screen (Alternative)

```bash
# Start bot in screen
screen -dmS ottbot bash -c "source .venv/bin/activate && python main.py"

# Reattach anytime
screen -r ottbot
```

**Note:** Screen sessions may not survive server reboots unless configured.

---

## 🧪 Test the Changes

1. **Start the bot**: `/start`
2. **Check prices**: Click "🎬 Buy OTTs"
3. **Verify each plan**:
   - Netflix 4K should show ₹75
   - Prime Video should show ₹35
   - YouTube Premium should show ₹25
   - Pornhub Premium should show ₹60
   - Combo Pack should show ₹125

---

## ❓ Troubleshooting

### Bot not starting?

```bash
# Check logs for errors
sudo journalctl -u ottbot -n 50

# Or if using screen/background
tail -50 bot.log
```

### Need to manually restart?

```bash
# Systemd
sudo systemctl restart ottbot

# Screen
screen -S ottbot -X quit
screen -dmS ottbot bash -c "source .venv/bin/activate && python main.py"

# Background process
kill $(cat bot.pid)
nohup .venv/bin/python main.py > bot.log 2>&1 &
```

### Check if Supabase is connected?

```bash
cd ~/ottsonly
source .venv/bin/activate
python test_supabase_connection.py
```

---

## 📞 Support

If you encounter any issues:

1. **Check bot logs** first
2. **Verify .env file** has correct credentials
3. **Ensure port 443/8443** is open (for Telegram)
4. **Check Supabase connection** is working

---

## 🎯 Future Updates

Whenever you need to update prices or make changes:

1. **Edit locally** (already done)
2. **Push to GitHub**: `git push origin main`
3. **Run on VPS**: `bash deploy_update.sh`

**Easy!** 🚀

---

## ✨ That's It!

Your bot is now running with the new prices and will stay online 24/7!

New prices are live:
- 📺 Netflix 4K: **₹75**
- 🎬 Prime Video: **₹35**
- 🎵 YouTube Premium: **₹25**
- 🔥 Pornhub Premium: **₹60**
- 🎁 Combo Pack: **₹125**
