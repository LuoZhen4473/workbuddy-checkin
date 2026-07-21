#!/bin/bash
# WorkBuddy 签到脚本 - macOS 安装依赖

echo "============================================"
echo "  WorkBuddy 签到脚本 - macOS 安装依赖"
echo "============================================"
echo ""

# 检查 Python 是否安装
if ! command -v python3 &> /dev/null; then
    echo "未找到 python3，请先安装 Python 3："
    echo "  brew install python3"
    echo "或从 https://www.python.org/downloads/ 下载"
    exit 1
fi

echo "正在安装 pyautogui、Pillow 和 opencv-python..."
pip3 install pyautogui Pillow opencv-python pyobjc-core pyobjc-framework-Quartz

echo ""
echo "依赖安装完成！"
echo ""
echo "============================================"
echo "  重要：macOS 权限设置"
echo "============================================"
echo ""
echo "脚本运行需要以下权限，请在「系统设置 > 隐私与安全」中授权："
echo ""
echo "  1. 辅助功能：授权你的终端应用（Terminal.app 或 iTerm2）"
echo "  2. 屏幕录制：授权你的终端应用"
echo ""
echo "============================================"
echo "  准备参考截图"
echo "============================================"
echo ""
echo "  1. 手动打开 WorkBuddy 并登录"
echo "  2. 用 Cmd+Shift+4 截取你的【头像+用户名】区域"
echo "     保存为 images/mac_avatar.png"
echo "  3. 点击头像打开签到面板，截取【领取】按钮"
echo "     保存为 images/mac_claim_button.png"
echo ""
echo "截图准备好后，运行 ./run_checkin.sh 即可执行签到！"
