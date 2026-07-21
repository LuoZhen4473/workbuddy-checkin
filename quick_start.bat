@echo off
chcp 65001 >nul
echo ============================================
echo   WorkBuddy 签到脚本 - 一键启动
echo ============================================
echo.

cd /d "%~dp0"

:: ========== 第1步：检查 Python ==========
echo [1/3] 检查 Python 环境...

py --version >nul 2>&1
if %errorlevel%==0 (
    echo       Python 已安装。
    goto :install_deps
)

python --version >nul 2>&1
if %errorlevel%==0 (
    echo       Python 已安装。
    goto :install_deps
)

echo       未检测到 Python，正在自动安装...
echo.

:: 尝试使用 winget 安装 Python
winget --version >nul 2>&1
if %errorlevel%==0 (
    echo       使用 winget 安装 Python 3...
    winget install Python.Python.3.13 --accept-package-agreements --accept-source-agreements
    if %errorlevel%==0 (
        echo       Python 安装成功！
        echo       正在刷新环境变量...
        :: 刷新 PATH
        set "PATH=%LOCALAPPDATA%\Programs\Python\Python313;%LOCALAPPDATA%\Programs\Python\Python313\Scripts;%PATH%"
        goto :install_deps
    ) else (
        echo       winget 安装失败。
    )
) else (
    echo       未检测到 winget。
)

:: winget 不可用或失败，提示手动安装
echo.
echo ============================================
echo   自动安装 Python 失败，请手动安装：
echo   下载地址: https://www.python.org/downloads/
echo   安装时请勾选 "Add Python to PATH"
echo ============================================
echo.
pause
exit /b 1

:: ========== 第2步：安装依赖 ==========
:install_deps
echo.
echo [2/3] 检查并安装 Python 依赖...

:: 检测 py 或 python 命令
set PYTHON_CMD=py
py --version >nul 2>&1
if %errorlevel% neq 0 (
    set PYTHON_CMD=python
)

:: 检查是否已安装 pyautogui
%PYTHON_CMD% -c "import pyautogui" >nul 2>&1
if %errorlevel%==0 (
    echo       依赖已安装，跳过。
    goto :run_checkin
)

echo       正在安装 pyautogui, Pillow, opencv-python...
%PYTHON_CMD% -m pip install pyautogui Pillow opencv-python --quiet
if %errorlevel%==0 (
    echo       依赖安装成功！
) else (
    echo       依赖安装失败，请手动运行: pip install pyautogui Pillow opencv-python
    pause
    exit /b 1
)

:: ========== 第3步：运行签到 ==========
:run_checkin
echo.
echo [3/3] 启动签到脚本...
echo.

%PYTHON_CMD% checkin.py

echo.
echo 脚本执行完毕，10 秒后自动关闭...
timeout /t 10 >nul
