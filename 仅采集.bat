@echo off
chcp 65001 >nul
cd /d "%~dp0"
title AI模型日报 - 仅采集

echo 正在采集各平台数据（不发送邮件）...
python main.py --collect-only
echo.
pause
