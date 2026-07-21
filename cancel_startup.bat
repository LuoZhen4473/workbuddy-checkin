@echo off
chcp 65001 >nul
echo 正在取消 WorkBuddy 签到脚本的开机自启动...
schtasks /delete /tn "WorkBuddy_Daily_Checkin" /f
if %errorlevel%==0 (
    echo 已成功取消开机自启动。
) else (
    echo 取消失败或任务不存在。
)
pause
