#!/bin/bash
# ============================================
# OTTsOnly Bot - Update & Restart Script
# ============================================
# This script pulls latest changes from GitHub
# and restarts the bot service
#
# Usage: bash deploy_update.sh
# ============================================

set -e

echo "🚀 Starting bot update process..."
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "${YELLOW}📂 Current directory: $SCRIPT_DIR${NC}"
echo ""

# Step 1: Pull latest changes from GitHub
echo -e "${YELLOW}📥 Pulling latest changes from GitHub...${NC}"
git fetch origin
git pull origin main

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Code updated successfully${NC}"
else
    echo -e "${RED}❌ Failed to pull changes${NC}"
    exit 1
fi
echo ""

# Step 2: Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}🔧 Creating virtual environment...${NC}"
    python3 -m venv .venv
fi

# Step 3: Activate virtual environment and update dependencies
echo -e "${YELLOW}📦 Updating dependencies...${NC}"
source .venv/bin/activate
pip install -r requirements.txt --upgrade --quiet

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Dependencies updated${NC}"
else
    echo -e "${RED}❌ Failed to update dependencies${NC}"
fi
echo ""

# Step 4: Check if bot is running as systemd service
if systemctl is-active --quiet ottbot; then
    echo -e "${YELLOW}🔄 Restarting systemd service...${NC}"
    sudo systemctl restart ottbot
    sleep 2
    
    if systemctl is-active --quiet ottbot; then
        echo -e "${GREEN}✅ Bot service restarted successfully${NC}"
        echo ""
        echo "📊 Service Status:"
        sudo systemctl status ottbot --no-pager -l | head -10
    else
        echo -e "${RED}❌ Bot service failed to start${NC}"
        echo "📋 Last 20 log lines:"
        sudo journalctl -u ottbot -n 20 --no-pager
        exit 1
    fi
    
# Step 5: If systemd not available, check for screen session
elif screen -ls | grep -q "ottbot"; then
    echo -e "${YELLOW}🔄 Restarting screen session...${NC}"
    screen -S ottbot -X quit 2>/dev/null || true
    sleep 1
    screen -dmS ottbot bash -c "source .venv/bin/activate && python main.py"
    sleep 2
    
    if screen -ls | grep -q "ottbot"; then
        echo -e "${GREEN}✅ Bot restarted in screen session${NC}"
        echo ""
        echo "ℹ️ Reattach with: screen -r ottbot"
    else
        echo -e "${RED}❌ Failed to start screen session${NC}"
        exit 1
    fi
    
# Step 6: If neither systemd nor screen, start fresh
else
    echo -e "${YELLOW}⚠️ Bot is not running. Starting new instance...${NC}"
    
    # Check if screen is available
    if command -v screen &> /dev/null; then
        screen -dmS ottbot bash -c "source .venv/bin/activate && python main.py"
        sleep 2
        
        if screen -ls | grep -q "ottbot"; then
            echo -e "${GREEN}✅ Bot started in screen session${NC}"
            echo ""
            echo "ℹ️ Reattach with: screen -r ottbot"
        else
            echo -e "${RED}❌ Failed to start bot${NC}"
            exit 1
        fi
    else
        echo -e "${YELLOW}🔧 Screen not found. Starting bot in background...${NC}"
        nohup .venv/bin/python main.py > bot.log 2>&1 &
        BOT_PID=$!
        sleep 2
        
        if ps -p $BOT_PID > /dev/null; then
            echo -e "${GREEN}✅ Bot started (PID: $BOT_PID)${NC}"
            echo ""
            echo "ℹ️ View logs: tail -f bot.log"
            echo "ℹ️ Stop bot: kill $BOT_PID"
            echo "$BOT_PID" > bot.pid
        else
            echo -e "${RED}❌ Failed to start bot${NC}"
            exit 1
        fi
    fi
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✨ Deployment completed successfully!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 Useful Commands:"
echo ""
echo "  Systemd:"
echo "    sudo systemctl status ottbot   # Check status"
echo "    sudo systemctl restart ottbot  # Restart"
echo "    sudo systemctl stop ottbot     # Stop"
echo "    sudo journalctl -u ottbot -f   # View logs"
echo ""
echo "  Screen:"
echo "    screen -r ottbot               # Reattach"
echo "    screen -ls                     # List sessions"
echo ""
echo "  Background Process:"
echo "    tail -f bot.log                # View logs"
echo "    kill \$(cat bot.pid)            # Stop bot"
echo ""
