@echo off
chcp 65001 >nul
cd /d "%~dp0"
title AI模型日报 - 安装依赖

echo 正在安装 Python 依赖包...
pip install -r requirements.txt
echo.
echo 安装完成！下一步请双击「配置邮箱.bat」
pause
