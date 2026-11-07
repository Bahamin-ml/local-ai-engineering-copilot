@echo off
title ML Engineering Copilot - Backend Server
cd /d "%~dp0"

echo ===================================================
echo   ML Engineering Copilot - Backend Launcher
echo ===================================================

echo [1/3] Activating Virtual Environment (rag_env)...
if exist "D:\venvs\rag_env\Scripts\activate.bat" (
    call "D:\venvs\rag_env\Scripts\activate.bat"
) else if exist "%~dp0rag_env\Scripts\activate.bat" (
    call "%~dp0rag_env\Scripts\activate.bat"
) else (
    echo [ERROR] Virtual environment not found at D:\venvs\rag_env
    pause
    exit /b 1
)

echo [2/3] Checking Ollama Service (127.0.0.1:11434)...
curl -s http://127.0.0.1:11434/api/tags >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo [OK] Ollama is active.
) else (
    echo [WARNING] Ollama is not responding on 127.0.0.1:11434.
    echo Please make sure the Ollama desktop app or service is running.
)

echo [3/3] Starting FastAPI Backend on http://127.0.0.1:8000 ...
python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8000 --reload

pause
