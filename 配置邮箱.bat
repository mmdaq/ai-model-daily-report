@echo off
chcp 65001 >nul
cd /d "%~dp0"
title AI模型日报 - 配置邮箱

python setup_env.py
pause
