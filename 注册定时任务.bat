@echo off
chcp 65001 >nul
cd /d "%~dp0"
title 注册 Windows 定时任务

echo.
echo 即将注册 Windows 任务计划：
echo   - 每天 08:00 自动发送日报
echo   - 若当时电脑关机，开机后自动补发
echo   - 无需保持窗口常开
echo.

powershell -ExecutionPolicy Bypass -File "%~dp0register_task.ps1"
echo.
pause
