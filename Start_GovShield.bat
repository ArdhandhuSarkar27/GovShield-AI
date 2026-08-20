@echo off
title GovShield AI Launcher
color 0B

echo.
echo  ============================================================
echo    .--.
echo   /.-. '----------.
echo   \'-' .--"--""-"-'
echo    '--'
echo    GOVSHIELD AI  v3.3  --  Ayushman Bharat Fraud Detection
echo  ============================================================
echo.

REM ── Detect where this script is located ────────────────────────
set "PROJECT_DIR=%~dp0"
cd /d "%PROJECT_DIR%"

echo  [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo  [ERROR] Python not found. Please install Python 3.9+ from:
    echo          https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version 2^>^&1') do echo         Found: %%i

echo.
echo  [2/5] Setting up virtual environment...
if not exist "venv" (
    echo         Creating new virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo  [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo         Done.
) else (
    echo         Existing venv found, skipping creation.
)

echo.
echo  [3/5] Activating environment and installing dependencies...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo  [ERROR] Failed to activate virtual environment.
    pause
    exit /b 1
)
pip install -r requirements.txt -q --no-warn-script-location
if errorlevel 1 (
    echo  [ERROR] Dependency installation failed. Check requirements.txt.
    pause
    exit /b 1
)
echo         All dependencies ready.

echo.
echo  [4/5] Generating data if needed...
if not exist "govshield_results.csv" (
    echo         No data file found - generating sample data...
    python main_simple.py >nul 2>&1
    if exist "govshield_results.csv" (
        echo         Sample data generated successfully.
    ) else (
        echo         Note: Could not auto-generate data.
        echo               Dashboard will show empty state until data is loaded.
    )
) else (
    echo         Data file found.
)

echo.
echo  [5/5] Starting GovShield server...
echo.
echo  ============================================================
echo    Server starting at:
echo      Dashboard : http://localhost:5000/dashboard
echo      Landing   : http://localhost:5000/landing
echo      AI Chat   : http://localhost:5000/dashboard
echo      Health    : http://localhost:5000/api/health
echo.
echo    NFHS-5 data loaded automatically from project folder.
echo    No API keys required - fully offline capable.
echo.
echo    Press Ctrl+C in this window to stop the server.
echo  ============================================================
echo.

REM ── Wait 2 seconds then open browser ──────────────────────────
timeout /t 2 > nul
start "" "http://localhost:5000/dashboard"

REM ── Start the Flask server (foreground so window stays open) ──
python flask_app.py

echo.
echo  GovShield has stopped.
pause
