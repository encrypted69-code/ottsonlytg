#!/bin/bash
# Auto deployment script - runs on VPS
set -e

echo "🚀 Starting OTTsOnly Bot VPS Deployment..."
apt update && apt upgrade -y

echo "📥 Installing dependencies..."
apt install -y python3.11 python3.11-venv python3-pip git screen

echo "📂 Cloning repository..."
cd ~
if [ -d "ottsonlytg" ]; then
    echo "⚠️  Directory exists, removing and re-cloning..."
    rm -rf ottsonlytg
fi
git clone https://github.com/encrypted69-code/ottsonlytg.git
cd ottsonlytg

echo "🐍 Creating Python virtual environment..."
python3.11 -m venv .venv

echo "📚 Installing Python packages..."
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "⚙️  Creating .env configuration file..."
cat > .env << 'EOL'
BOT_TOKEN=7412404145:AAEeu1uum9loSCU1ytqA0UmR-7yUOp-QgjI
ADMIN_ID=7127370646
SUPABASE_URL=https://dvbeelunzmkzbrshtoey.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR2YmVlbHVuem1remJyc2h0b2V5Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczNjc0OTA3MywiZXhwIjoyMDUyMzI1MDczfQ.sb_secret_-kVatCHbUKyMua8qYmlYnw_NfDpRpcp
EOL

echo ""
echo "✅ Setup complete! Bot is ready to run."
echo ""
echo "To start the bot with screen:"
echo "  screen -S ottbot"
echo "  cd ~/ottsonlytg"
echo "  source .venv/bin/activate"
echo "  python main.py"
echo "  # Press Ctrl+A then D to detach"
echo ""
echo "Or setup as systemd service for auto-restart:"
echo "  cd ~/ottsonlytg"
echo "  sudo bash setup_systemd.sh"
