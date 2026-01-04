#!/bin/bash
# OTTsOnly Bot VPS Setup Script
# Run this on your VPS after SSHing in

set -e  # Exit on any error

echo "🚀 Starting OTTsOnly Bot VPS Deployment..."

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install dependencies
echo "📥 Installing Python 3.11 and Git..."
sudo apt install -y python3.11 python3.11-venv python3-pip git screen

# Clone repository
echo "📂 Cloning repository..."
cd ~
if [ -d "ottsonlytg" ]; then
    echo "⚠️  Directory exists, pulling latest changes..."
    cd ottsonlytg
    git pull
else
    git clone https://github.com/encrypted69-code/ottsonlytg.git
    cd ottsonlytg
fi

# Create virtual environment
echo "🐍 Creating Python virtual environment..."
python3.11 -m venv .venv

# Activate and install dependencies
echo "📚 Installing Python packages..."
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file
echo ""
echo "⚙️  Creating .env configuration file..."
if [ ! -f ".env" ]; then
    cat > .env << 'EOL'
# Telegram Bot Configuration
BOT_TOKEN=7412404145:AAEeu1uum9loSCU1ytqA0UmR-7yUOp-QgjI
ADMIN_ID=7127370646

# Supabase Configuration
SUPABASE_URL=https://dvbeelunzmkzbrshtoey.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR2YmVlbHVuem1remJyc2h0b2V5Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczNjc0OTA3MywiZXhwIjoyMDUyMzI1MDczfQ.sb_secret_-kVatCHbUKyMua8qYmlYnw_NfDpRpcp
EOL
    echo "✅ .env file created"
else
    echo "✅ .env file already exists"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎯 Next steps:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Option 1: Run with Screen (for testing)"
echo "  screen -S ottbot"
echo "  cd ~/ottsonlytg"
echo "  source .venv/bin/activate"
echo "  python main.py"
echo "  # Press Ctrl+A then D to detach"
echo ""
echo "Option 2: Setup systemd service (recommended)"
echo "  sudo bash setup_systemd.sh"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
