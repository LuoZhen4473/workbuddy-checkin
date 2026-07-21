@echo off
chcp 65001 >nul
echo WorkBuddy 每日签到脚本运行中...
cd /d "%~dp0"
py checkin.py
echo.
echo 脚本执行完毕，5 秒后自动关闭...
timeout /t 5 >nul
