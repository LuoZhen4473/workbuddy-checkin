#!/bin/bash
# WorkBuddy 签到脚本 - macOS 运行入口

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "WorkBuddy 每日签到脚本运行中..."
python3 checkin.py
echo ""
echo "脚本执行完毕。"
