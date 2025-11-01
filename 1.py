#!/usr/bin/env python3

import time
import subprocess
import sys

# 目标设备序列号
DEVICE = "127.0.0.1:16384"

def adb_click(x, y):
    """通过ADB执行点击操作"""
    subprocess.run(
        ["adb", "-s", DEVICE, "shell", f"input tap {x} {y}"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

def adb_swipe(x1, y1, x2, y2, duration=0.8):
    """通过ADB执行滑动操作（duration单位：秒）"""
    # ADB滑动命令的duration单位是毫秒
    duration_ms = int(duration * 1000)
    subprocess.run(
        ["adb", "-s", DEVICE, "shell", f"input swipe {x1} {y1} {x2} {y2} {duration_ms}"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

for i in range(10):
    # 执行截图和匹配脚本
    subprocess.run([sys.executable, "screenshot.py"], check=True)
    subprocess.run([sys.executable, "pipei.py"], check=True)

    # 滑动操作（使用ADB实现）
    adb_swipe(900, 1800, 100, 200, 0.8)
    adb_click(260, 1300)

    # 循环点击操作
    for j in range(10):
        adb_click(670, 345)
        adb_click(978, 170)
        adb_click(412, 584)
        adb_click(1519, 112)
        adb_click(1773, 304)
        adb_click(1833, 1091)
        adb_click(737, 1085)
        print(f"第 {j+1}/10 次点击序列")
        time.sleep(0.5)

# 延迟后执行的点击操作
time.sleep(60)
adb_click(186, 1070)
adb_click(1546, 919)
adb_click(1283, 1230)