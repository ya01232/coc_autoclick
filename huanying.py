#!/usr/bin/env python3
import os
import sys
import time
import subprocess
import cv2

DEVICE = os.getenv("DEVICE", "127.0.0.1:16384")
THRESHOLD = float(os.getenv("THRESHOLD", "0.25"))
UI_DIR = "./ui"
SCREENSHOT_PATH = "screenshot.png"


def adb_click(x, y):
    try:
        subprocess.run(
            ["adb", "-s", DEVICE, "shell", "input", "tap", str(x), str(y)],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=5
        )
        return True
    except Exception as e:
        print(f"[ADB] 点击失败 ({x},{y}): {e}")
        return False


def send_simple_message():
    """直接发送：你好，常驻加订选"""
    try:
        subprocess.run(
            ["adb", "-s", DEVICE, "shell", "input", "text", "你好，常驻加订选"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=5
        )
        print("已输入: 你好，常驻加订选")
        return True
    except Exception as e:
        print(f"输入失败: {e}")
        return False


def take_screenshot_via_script():
    if not os.path.isfile("screenshot.py"):
        print("缺少 screenshot.py")
        return False
    try:
        subprocess.run([sys.executable, "screenshot.py", DEVICE], check=True, timeout=10)
    except Exception as e:
        print(f"截图失败: {e}")
        return False
    for _ in range(10):
        if os.path.isfile(SCREENSHOT_PATH) and os.path.getsize(SCREENSHOT_PATH) > 100:
            return True
        time.sleep(0.1)
    return False


def find_template(template_name):
    img = cv2.imread(SCREENSHOT_PATH)
    if img is None:
        return None
    tmpl_path = os.path.join(UI_DIR, template_name)
    tmpl = cv2.imread(tmpl_path)
    if tmpl is None:
        return None
    try:
        res = cv2.matchTemplate(img, tmpl, cv2.TM_SQDIFF_NORMED)
        min_val, _, min_loc, _ = cv2.minMaxLoc(res)
        h, w = tmpl.shape[:2]
        if min_val <= THRESHOLD:
            return (min_loc[0] + w // 2, min_loc[1] + h // 2)
    except:
        pass
    return None


def main():
    print(f"设备: {DEVICE}")
    print("回复内容: 你好，常驻加订选")
    print("-" * 35)

    for name in ["jiaru.png", "xiaoxi.png", "gou.png"]:
        if not os.path.isfile(os.path.join(UI_DIR, name)):
            print(f"缺少模板: {name}"); sys.exit(1)
    if not os.path.isfile("screenshot.py"):
        print("缺少 screenshot.py"); sys.exit(1)

    # 连接设备
    try:
        subprocess.run(["adb", "connect", DEVICE], timeout=3, 
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        pass

    print("开始监控...")

    try:
        while True:
            if not take_screenshot_via_script():
                time.sleep(1)
                continue

            jiaru_pos = find_template("jiaru.png")
            if jiaru_pos:
                print(f"检测到「加入」@ ({jiaru_pos[0]}, {jiaru_pos[1]})")

                # 点击消息框
                xiaoxi_pos = None
                for _ in range(3):
                    if take_screenshot_via_script():
                        xiaoxi_pos = find_template("xiaoxi.png")
                        if xiaoxi_pos:
                            break
                    time.sleep(0.3)
                if not xiaoxi_pos:
                    print("未找到消息框，跳过")
                    time.sleep(2)
                    continue

                print(f"点击消息框 @ {xiaoxi_pos}")
                adb_click(*xiaoxi_pos)
                time.sleep(0.5)

                send_simple_message()
                time.sleep(1.0)

                gou_pos = None
                for _ in range(5):
                    if take_screenshot_via_script():
                        gou_pos = find_template("gou.png")
                        if gou_pos:
                            break
                    time.sleep(0.3)
                if gou_pos:
                    print(f"点击「√」@ {gou_pos}")
                    adb_click(*gou_pos)
                else:
                    print("未找到「√」")

                time.sleep(60.0)
            else:
                time.sleep(0.5)

    except KeyboardInterrupt:
        print("\n退出")
    finally:
        try:
            if os.path.exists(SCREENSHOT_PATH):
                os.remove(SCREENSHOT_PATH)
        except:
            pass


if __name__ == "__main__":
    try:
        import cv2
    except ImportError:
        print("请运行: pip install opencv-python"); sys.exit(1)
    main()