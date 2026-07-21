#!/bin/bash
# WorkBuddy 签到脚本 - macOS 取消开机自启动

PLIST_NAME="com.user.workbuddy-checkin"
PLIST_PATH="$HOME/Library/LaunchAgents/${PLIST_NAME}.plist"

echo "正在取消 WorkBuddy 签到脚本的开机自启动..."

if [ -f "$PLIST_PATH" ]; then
    launchctl unload "$PLIST_PATH" 2>/dev/null
    rm -f "$PLIST_PATH"
    echo "已成功取消开机自启动。"
else
    echo "未找到自启动配置文件，可能已经取消或从未设置。"
fi
