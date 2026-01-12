@echo off
echo ================================================
echo    OTT REFERRAL SYSTEM - WINDOWS SETUP
echo ================================================
echo.

echo [1/4] Checking Python...
python --version
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.9+
    pause
    exit /b 1
)

echo.
echo [2/4] Creating virtual environment...
cd backend
python -m venv venv
call venv\Scripts\activate

echo.
echo [3/4] Installing dependencies...
pip install -r requirements.txt

echo.
echo [4/4] Creating environment file...
if not exist .env (
    copy .env.example .env
    echo .env file created. Please edit it with your settings.
)

echo.
echo ================================================
echo    BACKEND SETUP COMPLETE!
echo ================================================
echo.
echo Next steps:
echo 1. Edit backend\.env with your database and settings
echo 2. Create database: createdb ottsonly_referral
echo 3. Run schema: psql -d ottsonly_referral -f ..\database\schema.sql
echo 4. Start backend: cd backend ^& venv\Scripts\activate ^& uvicorn app.main:app --reload
echo 5. Setup frontend: cd frontend ^& npm install ^& npm run dev
echo.
echo For detailed instructions, see QUICKSTART.md
echo.
pause
