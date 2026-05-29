@echo off
chcp 65001 >nul
cd /d "%~dp0"

if not exist "logs" mkdir logs
set LOG=logs\send_%date:~0,4%%date:~5,2%%date:~8,2%.log

echo [%date% %time%] Start >> "%LOG%"
python main.py --once >> "%LOG%" 2>&1
echo [%date% %time%] Done >> "%LOG%"
