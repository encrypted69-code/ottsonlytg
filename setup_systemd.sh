#!/bin/bash
# Setup systemd service for OTTsOnly Bot
# Run with: sudo bash setup_systemd.sh

set -e

echo "🔧 Setting up systemd service..."

# Get current user
CURRENT_USER=$(whoami)
WORK_DIR="$(pwd)"

# Create systemd service file
cat > /tmp/ottbot.service << EOL
[Unit]
Description=OTTsOnly Telegram Bot
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$WORK_DIR
Environment="PATH=$WORK_DIR/.venv/bin"
ExecStart=$WORK_DIR/.venv/bin/python main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOL

# Move to systemd directory
sudo mv /tmp/ottbot.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable ottbot

# Start service
sudo systemctl start ottbot

echo ""
echo "✅ Systemd service setup complete!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 Service Management Commands:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  Check status:   sudo systemctl status ottbot"
echo "  View logs:      sudo journalctl -u ottbot -f"
echo "  Restart:        sudo systemctl restart ottbot"
echo "  Stop:           sudo systemctl stop ottbot"
echo "  Start:          sudo systemctl start ottbot"
echo "  Disable:        sudo systemctl disable ottbot"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🎉 Bot is now running 24/7!"
