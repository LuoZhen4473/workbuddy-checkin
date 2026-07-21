@echo off
chcp 65001 >nul
echo ============================================
echo   WorkBuddy 签到脚本 - 设置开机自启动
echo ============================================
echo.

set SCRIPT_DIR=%~dp0
set BAT_PATH=%SCRIPT_DIR%quick_start.bat

echo 将创建 Windows 计划任务，在每次登录时自动运行签到脚本。
echo 任务名称: WorkBuddy_Daily_Checkin
echo 脚本路径: %BAT_PATH%
echo 延迟: 登录后 30 秒执行（等待桌面加载完成）
echo.

:: 删除已有同名任务（如果存在）
schtasks /delete /tn "WorkBuddy_Daily_Checkin" /f >nul 2>&1

:: 创建计划任务：用户登录时运行，延迟 30 秒
schtasks /create /tn "WorkBuddy_Daily_Checkin" /tr "\"%BAT_PATH%\"" /sc ONLOGON /delay 0000:30 /rl HIGHEST /f

if %errorlevel%==0 (
    echo.
    echo 开机自启动设置成功！
    echo 每次登录后 30 秒，脚本将自动运行签到。
    echo.
    echo 如需取消，请运行: cancel_startup.bat
    echo 或手动删除计划任务: schtasks /delete /tn "WorkBuddy_Daily_Checkin" /f
) else (
    echo.
    echo 设置失败，请尝试以管理员身份运行此脚本。
)
echo.
pause
