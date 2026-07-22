"""
WorkBuddy 每日签到自动化脚本（跨平台版）
=========================================
支持 Windows 和 macOS。

功能：自动打开 WorkBuddy，识别头像/用户名并点击，再识别"领取"按钮并点击完成签到。

使用方法：
  1. 安装依赖：pip install pyautogui Pillow opencv-python
  2. 准备两张参考截图，放入 images/ 文件夹：
     Windows:  avatar.png, claim_button.png
     macOS:    mac_avatar.png, mac_claim_button.png
       (macOS Retina 屏幕像素密度不同，需要单独截图)
  3. 运行脚本：python checkin.py

如何获取参考截图：
  1) 手动打开 WorkBuddy 并登录
  2) 截取你的头像和用户名区域，保存为 avatar.png (Win) 或 mac_avatar.png (Mac)
  3) 点击头像打开签到面板，截取"领取"按钮，保存为 claim_button.png / mac_claim_button.png
  4) 将图片放入 images/ 文件夹

macOS 额外注意事项：
  - 需要在「系统设置 > 隐私与安全 > 辅助功能」中授权终端/Python
  - 需要在「系统设置 > 隐私与安全 > 屏幕录制」中授权终端/Python
"""

import subprocess
import time
import sys
import os
import platform
import logging
from datetime import datetime

# ========== 平台检测 ==========
IS_MACOS = platform.system() == "Darwin"
IS_WINDOWS = platform.system() == "Windows"

# Windows 平台需要 ctypes 调用 Win32 API 操作窗口
if IS_WINDOWS:
    import ctypes

# 配置日志
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

log_file = os.path.join(LOG_DIR, f"checkin_{datetime.now().strftime('%Y%m%d')}.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)

# ========== 配置区域 ==========
if IS_MACOS:
    WORKBUDDY_PATH = "/Applications/WorkBuddy.app"
    AVATAR_IMAGE_NAME = "mac_avatar.png"
    CLAIM_BUTTON_IMAGE_NAME = "mac_claim_button.png"
elif IS_WINDOWS:
    WORKBUDDY_PATH = r"C:\Program Files\WorkBuddy\WorkBuddy.exe"
    AVATAR_IMAGE_NAME = "avatar.png"
    CLAIM_BUTTON_IMAGE_NAME = "claim_button.png"
else:
    logger.error(f"不支持的操作系统: {platform.system()}")
    sys.exit(1)

IMAGES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
AVATAR_IMAGE = os.path.join(IMAGES_DIR, AVATAR_IMAGE_NAME)
CLAIM_BUTTON_IMAGE = os.path.join(IMAGES_DIR, CLAIM_BUTTON_IMAGE_NAME)

# 等待时间（秒）
APP_LAUNCH_WAIT = 12 if IS_MACOS else 10  # 登录时桌面加载可能较慢
WINDOW_WAIT_TIMEOUT = 60                  # 等待 WorkBuddy 窗口出现的最大秒数
SCREEN_GRAB_RETRY_DELAY = 5               # screen grab failed 时的额外等待
CLICK_WAIT = 2
MAX_SEARCH_ATTEMPTS = 15                  # 登录场景下增加重试次数
SEARCH_INTERVAL = 2
CONFIDENCE = 0.8
# ==============================


def check_dependencies():
    """检查必要的依赖是否已安装"""
    try:
        import pyautogui
        from PIL import Image
        return True
    except ImportError as e:
        logger.error(f"缺少依赖: {e}")
        logger.error("请运行: pip install pyautogui Pillow opencv-python")
        return False


def check_macos_permissions():
    """检查 macOS 上必要的权限"""
    if not IS_MACOS:
        return True

    warnings = []

    # 检查辅助功能权限 - 尝试使用 pyautogui
    try:
        import pyautogui
        pyautogui.position()
    except Exception:
        warnings.append(
            "  - 辅助功能权限: 请在「系统设置 > 隐私与安全 > 辅助功能」中授权你的终端应用"
        )

    # 检查屏幕录制权限 - 尝试截屏
    try:
        import pyautogui
        screenshot = pyautogui.screenshot()
        if screenshot.size == (0, 0):
            raise Exception("空截图")
    except Exception:
        warnings.append(
            "  - 屏幕录制权限: 请在「系统设置 > 隐私与安全 > 屏幕录制」中授权你的终端应用"
        )

    if warnings:
        logger.warning("检测到以下权限可能未授权：")
        for w in warnings:
            logger.warning(w)
        logger.warning("如果后续识图失败，请先授权上述权限。")

    return True


def check_reference_images():
    """检查参考截图是否存在"""
    missing = []
    platform_label = "macOS" if IS_MACOS else "Windows"
    for name, path in [
        (f"头像截图 ({AVATAR_IMAGE_NAME})", AVATAR_IMAGE),
        (f"领取按钮截图 ({CLAIM_BUTTON_IMAGE_NAME})", CLAIM_BUTTON_IMAGE),
    ]:
        if not os.path.isfile(path):
            missing.append(f"  - {name}: {path}")
    if missing:
        logger.error(f"缺少以下 {platform_label} 参考截图：")
        for m in missing:
            logger.error(m)
        logger.error("请在当前系统上截取参考图片并保存到 images/ 文件夹。")
        return False
    return True


def bring_workbuddy_to_front():
    """将 WorkBuddy 窗口置顶，确保能被截图识别"""
    if IS_MACOS:
        # macOS: 使用 osascript 激活应用
        try:
            subprocess.run([
                "osascript", "-e",
                'tell application "WorkBuddy" to activate'
            ], check=False, timeout=5)
            return True
        except Exception as e:
            logger.warning(f"macOS 置顶 WorkBuddy 失败: {e}")
            return False
    else:
        # Windows: 使用 ctypes 直接调用 Win32 API，比 pygetwindow 更稳定
        try:
            user32 = ctypes.windll.user32
            hwnd = user32.FindWindowW(None, "WorkBuddy")
            if not hwnd:
                return False

            # SW_RESTORE = 9, SW_SHOW = 5
            user32.ShowWindow(hwnd, 9)
            user32.SetForegroundWindow(hwnd)

            # 再最大化一下确保露出来（如果窗口在屏幕外也有效）
            time.sleep(0.3)
            user32.ShowWindow(hwnd, 3)  # SW_MAXIMIZE = 3
            time.sleep(0.3)
            user32.SetForegroundWindow(hwnd)
            return True
        except Exception as e:
            logger.warning(f"Windows 置顶 WorkBuddy 失败: {e}")
            return False


def is_screen_grab_available():
    """检查当前是否可以正常截屏（用于登录后桌面未完全初始化的情况）"""
    try:
        import pyautogui
        screenshot = pyautogui.screenshot()
        return screenshot.size[0] > 0 and screenshot.size[1] > 0
    except Exception as e:
        logger.warning(f"当前无法截屏: {e}")
        return False


def wait_for_desktop_ready():
    """等待桌面准备好（可截屏）"""
    logger.info("正在等待桌面/屏幕准备就绪...")
    start = time.time()
    while time.time() - start < WINDOW_WAIT_TIMEOUT:
        if is_screen_grab_available():
            logger.info("桌面已准备就绪")
            return True
        time.sleep(2)
    logger.error("桌面长时间无法截屏，可能是权限或显示驱动未加载")
    return False


def wait_for_workbuddy_window():
    """等待 WorkBuddy 窗口出现并可交互"""
    logger.info("正在等待 WorkBuddy 窗口出现...")
    start = time.time()

    while time.time() - start < WINDOW_WAIT_TIMEOUT:
        if IS_MACOS:
            # macOS 简单等待
            time.sleep(1)
            return True
        else:
            # Windows: 使用 ctypes 检查窗口是否存在
            try:
                user32 = ctypes.windll.user32
                hwnd = user32.FindWindowW(None, "WorkBuddy")
                if hwnd:
                    logger.info("WorkBuddy 窗口已出现")
                    return True
            except Exception:
                pass
        time.sleep(1)

    logger.error(f"等待 {WINDOW_WAIT_TIMEOUT} 秒后仍未找到 WorkBuddy 窗口")
    return False


def launch_workbuddy():
    """启动 WorkBuddy 应用"""
    logger.info(f"正在启动 WorkBuddy...")

    if IS_MACOS:
        # macOS: 检查 .app 是否存在
        if not os.path.isdir(WORKBUDDY_PATH):
            logger.error(f"未找到 WorkBuddy 应用: {WORKBUDDY_PATH}")
            logger.error("请确认 WorkBuddy 已安装到 /Applications 目录。")
            return False
        try:
            subprocess.Popen(["open", "-a", "WorkBuddy"])
        except Exception as e:
            logger.error(f"启动 WorkBuddy 失败: {e}")
            return False

    else:
        # Windows
        if not os.path.isfile(WORKBUDDY_PATH):
            logger.error(f"未找到 WorkBuddy 可执行文件: {WORKBUDDY_PATH}")
            logger.error("请确认 WorkBuddy 已正确安装，或修改脚本中的 WORKBUDDY_PATH。")
            return False
        try:
            subprocess.Popen([WORKBUDDY_PATH])
        except Exception as e:
            logger.error(f"启动 WorkBuddy 失败: {e}")
            return False

    # 等待窗口出现
    if not wait_for_workbuddy_window():
        return False

    # 将窗口置顶
    if bring_workbuddy_to_front():
        logger.info("WorkBuddy 窗口已置顶")
    else:
        logger.warning("无法置顶 WorkBuddy 窗口，将继续尝试")

    # 等待桌面/屏幕准备就绪（登录时特别重要）
    if not wait_for_desktop_ready():
        return False

    # 再次置顶，确保在屏幕可用后被正确显示
    bring_workbuddy_to_front()

    logger.info(f"等待 {APP_LAUNCH_WAIT} 秒让 WorkBuddy 加载界面...")
    time.sleep(APP_LAUNCH_WAIT)
    return True


def find_and_click(image_path, description, confidence=None):
    """
    在屏幕上查找指定图像并点击。
    """
    import pyautogui

    if confidence is None:
        confidence = CONFIDENCE

    logger.info(f"正在搜索 [{description}]...")

    screen_grab_failures = 0

    for attempt in range(1, MAX_SEARCH_ATTEMPTS + 1):
        try:
            location = pyautogui.locateOnScreen(image_path, confidence=confidence)
            if location:
                center = pyautogui.center(location)
                logger.info(f"找到 [{description}]，位置: ({center.x}, {center.y})")
                pyautogui.click(center.x, center.y)
                logger.info(f"已点击 [{description}]")
                time.sleep(CLICK_WAIT)
                return True
        except pyautogui.ImageNotFoundException:
            pass
        except Exception as e:
            error_msg = str(e).lower()
            if "screen grab" in error_msg or "screencapture" in error_msg:
                screen_grab_failures += 1
                logger.warning(
                    f"搜索 [{description}] 第 {attempt} 次截屏失败 "
                    f"({screen_grab_failures})，等待 {SCREEN_GRAB_RETRY_DELAY} 秒..."
                )
                # 尝试重新置顶窗口并等待
                bring_workbuddy_to_front()
                time.sleep(SCREEN_GRAB_RETRY_DELAY)
                continue
            logger.warning(f"搜索 [{description}] 第 {attempt} 次出错: {e}")

        if attempt < MAX_SEARCH_ATTEMPTS:
            logger.info(
                f"未找到 [{description}]，第 {attempt}/{MAX_SEARCH_ATTEMPTS} 次尝试，"
                f"{SEARCH_INTERVAL} 秒后重试..."
            )
            time.sleep(SEARCH_INTERVAL)

    logger.error(f"未能找到 [{description}]，已尝试 {MAX_SEARCH_ATTEMPTS} 次。")
    logger.error(f"请确认参考截图 ({image_path}) 是否正确，或界面是否已加载完成。")
    return False


def do_checkin():
    """执行签到流程"""
    platform_name = "macOS" if IS_MACOS else "Windows"
    logger.info("=" * 50)
    logger.info(f"WorkBuddy 每日签到脚本启动 [{platform_name}]")
    logger.info(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 50)

    # 1. 检查依赖
    if not check_dependencies():
        return False

    # 2. macOS 权限检查
    if IS_MACOS:
        check_macos_permissions()

    # 3. 检查参考截图
    if not check_reference_images():
        return False

    # 4. 启动 WorkBuddy
    if not launch_workbuddy():
        return False

    # 5. 再次确保 WorkBuddy 在最前面
    bring_workbuddy_to_front()

    # 6. 点击头像/用户名（打开签到面板）
    if not find_and_click(AVATAR_IMAGE, "头像/用户名"):
        logger.error("未能识别头像，可能原因：")
        logger.error("  1. WorkBuddy 未登录或界面未加载完成")
        logger.error("  2. 当前有全屏应用（如游戏）遮挡了 WorkBuddy 窗口")
        logger.error("  3. 参考截图 avatar.png 与实际界面不符")
        logger.error("  4. 屏幕分辨率/DPI 缩放发生变化")
        logger.error("  5. 登录后桌面尚未完全初始化（请增加计划任务延迟时间）")
        return False

    # 7. 点击"领取"按钮
    if not find_and_click(CLAIM_BUTTON_IMAGE, "领取按钮"):
        return False

    logger.info("=" * 50)
    logger.info("签到完成！已成功领取 100 免费额度。")
    logger.info("=" * 50)
    return True


if __name__ == "__main__":
    success = do_checkin()
    if not success:
        logger.error("签到未成功，请检查日志了解详情。")
        sys.exit(1)
    sys.exit(0)
