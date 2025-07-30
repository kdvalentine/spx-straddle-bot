@echo off
echo ======================================
echo SPX Straddle Bot - Quick Start Setup
echo ======================================
echo.

REM Step 1: Check Python
echo Step 1: Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)
echo Python is installed!
echo.

REM Step 2: Create virtual environment
echo Step 2: Setting up Python environment...
if not exist venv (
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
call venv\Scripts\activate

REM Install requirements
echo Installing required packages...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install packages
    pause
    exit /b 1
)

echo.
echo ======================================
echo Step 3: OpenD Installation
echo ======================================
echo.
echo You need to install OpenD (moomoo's API gateway).
echo.
echo 1. Download OpenD from: https://www.moomoo.com/download/OpenAPI
echo 2. Install and run OpenD
echo 3. Log into your moomoo account in OpenD
echo 4. Keep OpenD running in the background
echo.
echo Press any key when OpenD is running and you're logged in...
pause >nul

REM Step 4: Get account info
echo.
echo ======================================
echo Step 4: Discovering Your Account IDs
echo ======================================
echo.
python scripts\get_account_info.py

echo.
echo ======================================
echo Step 5: Configuration
echo ======================================
echo.
echo Now you need to edit the .env file with:
echo 1. Your moomoo login credentials
echo 2. The account ID shown above
echo.

REM Copy template if .env doesn't exist
if not exist .env (
    copy .env.template .env
    echo Created .env file from template
)

echo Would you like to edit .env now? (y/n)
set /p response=
if /i "%response%"=="y" (
    notepad .env
)

REM Step 5: Test
echo.
echo ======================================
echo Step 6: Testing Your Setup
echo ======================================
echo.
echo Ready to test your configuration?
echo Press any key to run a connection test...
pause >nul

python src\production_strategy_complete.py --check-only

echo.
echo ======================================
echo Setup Complete!
echo ======================================
echo.
echo If the test was successful, you can now run the bot:
echo.
echo Paper trading (recommended):
echo   python src\production_strategy_complete.py --paper
echo.
echo Live trading (use with caution):
echo   python src\production_strategy_complete.py
echo.
echo For help, see the SIMPLE_SETUP_GUIDE.md file
pause