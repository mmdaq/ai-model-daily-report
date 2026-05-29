@echo off
chcp 65001 >nul
cd /d "%~dp0"
title AI模型日报 - 每天自动发送

if not exist ".env" (
    echo [提示] 尚未配置邮箱，正在启动配置向导...
    python setup_env.py
    if not exist ".env" exit /b 1
)

echo ========================================
echo   AI模型日报 - 定时守护模式
echo   每天 08:00 自动采集并发送邮件
echo   请保持此窗口不要关闭
echo ========================================
echo.
python main.py --daemon
