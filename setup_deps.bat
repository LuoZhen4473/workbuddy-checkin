@echo off
chcp 65001 >nul
echo ============================================
echo   WorkBuddy 签到脚本 - 安装依赖
echo ============================================
echo.
echo 正在安装 pyautogui 和 Pillow...
py -m pip install pyautogui Pillow opencv-python
echo.
echo 依赖安装完成！
echo.
echo 接下来请准备参考截图：
echo   1. 手动打开 WorkBuddy 并登录
echo   2. 用 Win+Shift+S 截取你的【头像+用户名】区域，保存为 images\avatar.png
echo   3. 点击头像打开签到面板，截取【领取】按钮，保存为 images\claim_button.png
echo.
echo 截图准备好后，运行 run_checkin.bat 即可执行签到！
pause
