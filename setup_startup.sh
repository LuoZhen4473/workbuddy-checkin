#!/bin/bash
# WorkBuddy 签到脚本 - macOS 设置开机自启动（使用 launchd）

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLIST_NAME="com.user.workbuddy-checkin"
PLIST_PATH="$HOME/Library/LaunchAgents/${PLIST_NAME}.plist"
LOG_DIR="${SCRIPT_DIR}/logs"

echo "============================================"
echo "  WorkBuddy 签到脚本 - macOS 开机自启动"
echo "============================================"
echo ""

# 确保日志目录存在
mkdir -p "$LOG_DIR"

# 如果已有 plist，先卸载
if launchctl list | grep -q "$PLIST_NAME" 2>/dev/null; then
    echo "检测到已有任务，正在卸载..."
    launchctl unload "$PLIST_PATH" 2>/dev/null
fi

# 生成 launchd plist 文件
cat > "$PLIST_PATH" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>${PLIST_NAME}</string>

    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>${SCRIPT_DIR}/quick_start.sh</string>
    </array>

    <key>RunAtLoad</key>
    <true/>

    <key>StartInterval</key>
    <integer>86400</integer>

    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
    </dict>

    <key>StandardOutPath</key>
    <string>${LOG_DIR}/launchd_stdout.log</string>

    <key>StandardErrorPath</key>
    <string>${LOG_DIR}/launchd_stderr.log</string>
</dict>
</plist>
EOF

echo "已生成 plist: $PLIST_PATH"
echo ""

# 加载任务
launchctl load "$PLIST_PATH"

if [ $? -eq 0 ]; then
    echo "开机自启动设置成功！"
    echo ""
    echo "  - 任务名称: ${PLIST_NAME}"
    echo "  - 运行时机: 每次登录后自动运行"
    echo "  - 日志位置: ${LOG_DIR}/"
    echo ""
    echo "如需取消，请运行: ./cancel_startup.sh"
else
    echo "设置失败，请检查权限。"
fi
