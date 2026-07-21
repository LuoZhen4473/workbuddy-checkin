#!/bin/bash
# WorkBuddy 签到脚本 - macOS 一键启动

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "============================================"
echo "  WorkBuddy 签到脚本 - macOS 一键启动"
echo "============================================"
echo ""

# ========== 第1步：检查 Python ==========
echo "[1/3] 检查 Python 环境..."

if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "      $PYTHON_VERSION 已安装。"
else
    echo "      未检测到 Python 3，正在尝试安装..."
    echo ""

    # 尝试使用 brew 安装
    if command -v brew &> /dev/null; then
        echo "      使用 Homebrew 安装 Python 3..."
        brew install python3
        if [ $? -eq 0 ]; then
            echo "      Python 安装成功！"
        else
            echo "      Homebrew 安装失败。"
            echo "      请手动安装: https://www.python.org/downloads/"
            exit 1
        fi
    else
        echo "      未检测到 Homebrew。"
        echo "      请先安装 Homebrew: https://brew.sh"
        echo "      或手动安装 Python: https://www.python.org/downloads/"
        echo ""
        read -p "      是否现在安装 Homebrew? (y/n): " choice
        if [ "$choice" = "y" ] || [ "$choice" = "Y" ]; then
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            # 刷新 PATH
            eval "$(/opt/homebrew/bin/brew shellenv 2>/dev/null || /usr/local/bin/brew shellenv 2>/dev/null)"
            echo "      正在安装 Python 3..."
            brew install python3
        else
            exit 1
        fi
    fi
fi

PYTHON_CMD="python3"

# ========== 第2步：安装依赖 ==========
echo ""
echo "[2/3] 检查并安装 Python 依赖..."

if $PYTHON_CMD -c "import pyautogui" 2>/dev/null; then
    echo "      依赖已安装，跳过。"
else
    echo "      正在安装 pyautogui, Pillow, opencv-python, pyobjc..."
    pip3 install pyautogui Pillow opencv-python pyobjc-core pyobjc-framework-Quartz --quiet
    if [ $? -eq 0 ]; then
        echo "      依赖安装成功！"
    else
        echo "      依赖安装失败，请手动运行:"
        echo "      pip3 install pyautogui Pillow opencv-python pyobjc-core pyobjc-framework-Quartz"
        exit 1
    fi
fi

# ========== 第3步：运行签到 ==========
echo ""
echo "[3/3] 启动签到脚本..."
echo ""

$PYTHON_CMD checkin.py

echo ""
echo "脚本执行完毕。"
