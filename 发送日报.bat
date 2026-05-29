@echo off
chcp 65001 >nul
cd /d "%~dp0"
title AI模型日报 - 发送一次

if not exist ".env" (
    echo [提示] 尚未配置邮箱，正在启动配置向导...
    python setup_env.py
    if not exist ".env" exit /b 1
)

echo 正在采集数据并发送日报邮件，请稍候...
python main.py --once --force
echo.
pause
