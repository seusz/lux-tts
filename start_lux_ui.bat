@echo off
title LuxTTS Voice Clone UI
chcp 65001 >nul
cd /d "%~dp0"
echo ========================================
echo   LuxTTS 语音克隆 Web UI
echo   http://127.0.0.1:7860
echo ========================================
echo.
echo Starting... (browser will open shortly)
start http://127.0.0.1:7860
set HF_HUB_OFFLINE=1
C:\Users\Administrator\anaconda3\envs\luxtts\python.exe lux_ui.py
pause
