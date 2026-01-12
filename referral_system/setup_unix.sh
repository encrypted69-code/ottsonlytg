#!/bin/bash

echo "================================================"
echo "   OTT REFERRAL SYSTEM - UNIX/MAC SETUP"
echo "================================================"
echo ""

echo "[1/4] Checking Python..."
python3 --version || {
    echo "ERROR: Python not found. Please install Python 3.9+"
    exit 1
}

echo ""
echo "[2/4] Creating virtual environment..."
cd backend
python3 -m venv venv
source venv/bin/activate

echo ""
echo "[3/4] Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "[4/4] Creating environment file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo ".env file created. Please edit it with your settings."
fi

echo ""
echo "================================================"
echo "   BACKEND SETUP COMPLETE!"
echo "================================================"
echo ""
echo "Next steps:"
echo "1. Edit backend/.env with your database and settings"
echo "2. Create database: createdb ottsonly_referral"
echo "3. Run schema: psql -d ottsonly_referral -f ../database/schema.sql"
echo "4. Start backend: cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo "5. Setup frontend: cd frontend && npm install && npm run dev"
echo ""
echo "For detailed instructions, see QUICKSTART.md"
echo ""
