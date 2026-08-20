@echo off
title GovShield AI - One-Click Launcher
color 0A
cls
setlocal enabledelayedexpansion

echo =========================================================================
echo  🛡️  GovShield AI v3.5 — Production Healthcare Fraud Detection System  🛡️
echo =========================================================================
echo.
echo  [1/5] Checking Environment ^& Dependencies...
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo  ❌ ERROR: Python is not detected in PATH. Please install Python 3.9+!
    pause
    exit /b 1
)
echo  ✅ Python runtime detected.

REM ── Read configured model from .env (falls back to default if not set) ──────
set "OLLAMA_MODEL=llama3.1:latest"
set "OLLAMA_BASE_URL=http://127.0.0.1:11434"
if exist ".env" (
    for /f "usebackq tokens=1,* delims==" %%A in (".env") do (
        if "%%A"=="OLLAMA_MODEL" if not "%%B"=="" set "OLLAMA_MODEL=%%B"
        if "%%A"=="OLLAMA_BASE_URL" if not "%%B"=="" set "OLLAMA_BASE_URL=%%B"
    )
)

echo.
echo  [2/5] Checking Local AI Engine (Ollama)...
where ollama >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo  ℹ️  Ollama CLI not found in PATH. GovShield will use Claude/rule-based chat instead.
    goto :start_backend
)
echo  ✅ Ollama CLI detected.

REM ── Check if Ollama is already responding — reuse it, don't start a duplicate ──
set "OLLAMA_UP=0"
curl -s -o nul -w "%%{http_code}" "%OLLAMA_BASE_URL%/api/tags" > "%TEMP%\govshield_ollama_check.txt" 2>nul
set /p OLLAMA_HTTP_CODE=<"%TEMP%\govshield_ollama_check.txt"
del "%TEMP%\govshield_ollama_check.txt" >nul 2>&1
if "%OLLAMA_HTTP_CODE%"=="200" (
    echo  ✅ Ollama is already running at %OLLAMA_BASE_URL% — reusing existing server.
    set "OLLAMA_UP=1"
) else (
    echo  🤖 Ollama not running yet — starting it now...
    start "Ollama Engine" /min cmd /c "ollama serve"

    echo  ⏳ Waiting for Ollama to become healthy...
    set "WAIT_TRIES=0"
    :wait_ollama
    set /a WAIT_TRIES+=1
    timeout /t 1 > nul
    curl -s -o nul -w "%%{http_code}" "%OLLAMA_BASE_URL%/api/tags" > "%TEMP%\govshield_ollama_check.txt" 2>nul
    set /p OLLAMA_HTTP_CODE=<"%TEMP%\govshield_ollama_check.txt"
    del "%TEMP%\govshield_ollama_check.txt" >nul 2>&1
    if "%OLLAMA_HTTP_CODE%"=="200" (
        echo  ✅ Ollama is now responding at %OLLAMA_BASE_URL%.
        set "OLLAMA_UP=1"
        goto :ollama_ready
    )
    if !WAIT_TRIES! LSS 15 goto :wait_ollama
    echo  ⚠️  Ollama did not respond after 15 seconds. GovShield will use Claude/rule-based chat instead.
)
:ollama_ready

if "%OLLAMA_UP%"=="1" (
    echo.
    echo  [3/5] Verifying configured model "%OLLAMA_MODEL%"...
    ollama list | findstr /C:"%OLLAMA_MODEL%" >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        echo  ✅ Model "%OLLAMA_MODEL%" is available.
    ) else (
        echo  ⚠️  Model "%OLLAMA_MODEL%" is NOT pulled yet.
        echo     GovShield will still start, but chat will fall back to Claude/rule-based
        echo     until you run:   ollama pull %OLLAMA_MODEL%
    )
) else (
    echo.
    echo  [3/5] Skipping model check — Ollama is not available.
)

:start_backend
echo.
echo  [4/5] Starting GovShield Flask Core Backend Server...
cd /d "%~dp0"
start "GovShield Core Backend" cmd /k "python flask_app.py"

echo.
echo  [5/5] Waiting for backend server startup on http://localhost:5000...
timeout /t 4 > nul

echo.
echo  =========================================================================
echo  🚀 GovShield AI System successfully launched!
echo  🌐 Dashboard URL:  http://localhost:5000/landing
echo  =========================================================================
echo.
start http://localhost:5000/landing

pause
