@echo off
title ML Engineering Copilot - Desktop Client
cd /d "%~dp0"

echo ===================================================
echo   ML Engineering Copilot - Desktop Client
echo ===================================================

echo [1/2] Activating Virtual Environment (rag_env)...
if exist "D:\venvs\rag_env\Scripts\activate.bat" (
    call "D:\venvs\rag_env\Scripts\activate.bat"
) else if exist "%~dp0rag_env\Scripts\activate.bat" (
    call "%~dp0rag_env\Scripts\activate.bat"
) else (
    echo [ERROR] Virtual environment not found at D:\venvs\rag_env
    pause
    exit /b 1
)

echo [2/2] Launching PyQt5 Desktop Application...
python -m desktop.main

pause
