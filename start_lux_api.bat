@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ==============================================
echo   LuxTTS OpenAI-Compat API Server
echo   http://0.0.0.0:8080
echo ==============================================
echo.
echo Starting... (Ctrl+C to stop)
set HF_HUB_OFFLINE=1
C:\Users\Administrator\anaconda3\envs\luxtts\python.exe lux_api.py
pause
