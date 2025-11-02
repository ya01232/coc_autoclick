#!/usr/bin/env python3

import time
import subprocess
import sys
import os
import cv2


# 全局变量存储当前模板的坐标
GLOBAL_X = None
GLOBAL_Y = None
# 目标设备序列号
DEVICE = "127.0.0.1:16384"
# 固定匹配阈值
FIXED_THRESHOLD = 0.25


def adb_click(x, y):
    """通过ADB执行点击操作"""
    try:
        subprocess.run(
            ["adb", "-s", DEVICE, "shell", f"input tap {x} {y}"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print(f"ADB点击成功：({x}, {y})")
    except subprocess.CalledProcessError as e:
        print(f"ADB点击失败：{e}")


def take_screenshot():
    """执行截图脚本并处理错误"""
    try:
        subprocess.run([sys.executable, "screenshot.py"], check=True)
        print("截图成功")
        time.sleep(0.5)  # 确保文件写入完成
        return True
    except subprocess.CalledProcessError as e:
        print(f"截图失败：{e}")
        return False
    except FileNotFoundError:
        print("未找到screenshot.py脚本")
        return False


def get_xy(img_model_path, retry=2):
    """
    匹配模板（使用固定阈值）并支持重试机制
    :param img_model_path: 模板路径
    :param retry: 匹配失败重试次数
    :return: 坐标或None
    """
    global GLOBAL_X, GLOBAL_Y
    img_path = "./screenshot.png"
    full_model_path = os.path.join("./ui/", img_model_path)
    
    # 检查模板文件是否存在
    if not os.path.exists(full_model_path):
        print(f"模板文件不存在：{full_model_path}")
        GLOBAL_X, GLOBAL_Y = None, None
        return None
    
    # 读取模板
    img_model = cv2.imread(full_model_path)
    if img_model is None:
        print(f"无法读取模板：{full_model_path}")
        GLOBAL_X, GLOBAL_Y = None, None
        return None
    model_h, model_w = img_model.shape[:2]

    # 支持重试机制（使用固定阈值）
    for attempt in range(retry + 1):
        # 读取原始图像（每次重试重新读取）
        img = cv2.imread(img_path)
        if img is None:
            print(f"无法读取截图 {img_path}（尝试 {attempt + 1}/{retry + 1}）")
            time.sleep(0.5)
            continue

        # 模板匹配（固定阈值）
        result = cv2.matchTemplate(img, img_model, cv2.TM_SQDIFF_NORMED)
        min_val, _, min_loc, _ = cv2.minMaxLoc(result)

        # 判断是否匹配成功（使用固定阈值）
        if min_val <= FIXED_THRESHOLD:
            GLOBAL_X = int(min_loc[0] + model_w / 2)
            GLOBAL_Y = int(min_loc[1] + model_h / 2)
            print(f"{img_model_path} 匹配成功（尝试 {attempt + 1}）：坐标 ({GLOBAL_X}, {GLOBAL_Y})，匹配值 {min_val:.4f}")
            return (GLOBAL_X, GLOBAL_Y)
        else:
            print(f"{img_model_path} 匹配失败（尝试 {attempt + 1}）：匹配值 {min_val:.4f} > 固定阈值 {FIXED_THRESHOLD}")
            if attempt < retry:
                time.sleep(0.5)  # 重试前等待

    # 所有重试都失败
    print(f"{img_model_path} 所有尝试均失败")
    GLOBAL_X, GLOBAL_Y = None, None
    return None


def process_templates(template_list, click_after_match=False):
    """
    依次处理模板（使用固定阈值）
    :param template_list: 模板列表
    :param click_after_match: 是否点击
    :return: 结果字典
    """
    result_dict = {}
    print(f"使用ADB连接设备：{DEVICE}，固定匹配阈值：{FIXED_THRESHOLD}")
    
    for template in template_list:
        print(f"\n===== 处理模板：{template} =====")
        # 1. 截图
        if not take_screenshot():
            result_dict[template] = None
            continue
        
        # 2. 使用固定阈值匹配（支持重试）
        coord = get_xy(template, retry=1)  # 可根据需要调整重试次数
        result_dict[template] = coord
        
        # 3. 点击（如果需要）
        if click_after_match and coord is not None:
            print(f"准备点击坐标：({GLOBAL_X}, {GLOBAL_Y})")
            adb_click(GLOBAL_X, GLOBAL_Y)
            time.sleep(1.5)  # 等待界面响应
        elif not coord:
            print(f" 跳过 {template} 点击（无有效坐标）")
    
    return result_dict


if __name__ == "__main__":
    templates_to_process = [
        "caoman.png",
        # 其他模板...
    ]
    
    results = process_templates(
        template_list=templates_to_process,
        click_after_match=True
    )
    
    print("\n 所有模板识别结果：")
    for name, coord in results.items():
        print(f"{name}: {coord}")