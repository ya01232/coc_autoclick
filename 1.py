#!/usr/bin/env python3

import time
import subprocess
import sys
import os
import cv2

# 全局配置
GLOBAL_X = None
GLOBAL_Y = None
DEVICE = "127.0.0.1:16384"
FIXED_THRESHOLD = 0.25
SCREENSHOT_PATH = "./screenshot.png"
UI_TEMPLATE_DIR = "./ui/"


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


def adb_swipe(x1, y1, x2, y2, duration=0.8):
    """通过ADB执行滑动操作（duration单位：秒）"""
    duration_ms = int(duration * 1000)
    try:
        subprocess.run(
            ["adb", "-s", DEVICE, "shell", f"input swipe {x1} {y1} {x2} {y2} {duration_ms}"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print(f"ADB滑动成功：({x1},{y1}) -> ({x2},{y2}) 耗时{duration}秒")
    except subprocess.CalledProcessError as e:
        print(f"ADB滑动失败：{e}")


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
    """匹配模板并支持重试机制"""
    global GLOBAL_X, GLOBAL_Y
    full_model_path = os.path.join(UI_TEMPLATE_DIR, img_model_path)
    
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

    # 支持重试机制
    for attempt in range(retry + 1):
        # 读取原始图像（每次重试重新读取）
        img = cv2.imread(SCREENSHOT_PATH)
        if img is None:
            print(f"无法读取截图 {SCREENSHOT_PATH}（尝试 {attempt + 1}/{retry + 1}）")
            time.sleep(0.5)
            continue

        # 模板匹配
        result = cv2.matchTemplate(img, img_model, cv2.TM_SQDIFF_NORMED)
        min_val, _, min_loc, _ = cv2.minMaxLoc(result)

        # 判断是否匹配成功
        if min_val <= FIXED_THRESHOLD:
            GLOBAL_X = int(min_loc[0] + model_w / 2)
            GLOBAL_Y = int(min_loc[1] + model_h / 2)
            print(f"{img_model_path} 匹配成功（尝试 {attempt + 1}）：坐标 ({GLOBAL_X}, {GLOBAL_Y})，匹配值 {min_val:.4f}")
            return (GLOBAL_X, GLOBAL_Y)
        else:
            print(f"{img_model_path} 匹配失败（尝试 {attempt + 1}）：匹配值 {min_val:.4f} > 阈值 {FIXED_THRESHOLD}")
            if attempt < retry:
                time.sleep(0.5)

    # 所有重试都失败
    print(f"{img_model_path} 所有尝试均失败")
    GLOBAL_X, GLOBAL_Y = None, None
    return None


def process_templates(template_list, click_after_match=False):
    result_dict = {}
    print(f"使用ADB连接设备：{DEVICE}，匹配阈值：{FIXED_THRESHOLD}")
    
    for template in template_list:
        print(f"\n===== 处理模板：{template} =====")
        # 1. 截图
        if not take_screenshot():
            result_dict[template] = None
            continue
        
        # 2. 模板匹配（支持重试）
        coord = get_xy(template, retry=1)
        result_dict[template] = coord
        
        # 3. 点击（如果需要）
        if click_after_match and coord is not None:
            print(f"准备点击坐标：({GLOBAL_X}, {GLOBAL_Y})")
            adb_click(GLOBAL_X, GLOBAL_Y)
            time.sleep(1)  # 等待界面响应
        elif not coord:
            print(f" 跳过 {template} 点击（无有效坐标）")
    
    return result_dict


def process_caoman():
    templates = ["caoman.png"]
    return process_templates(templates, click_after_match=True)


def process_pipei():
    templates = ["jingong.png", "sousuo.png"]
    return process_templates(templates, click_after_match=True)


def process_huijia():
    templates = ["jieshu.png", "queding.png", "huiying.png"]
    return process_templates(templates, click_after_match=True)

def process_nvhuang():
    templates = ["nvhuang.png"]
    return process_templates(templates, click_after_match=True)

def process_manwang():
    templates = ["manwang.png"]
    return process_templates(templates, click_after_match=True)

def process_yongwang():
    templates = ["yongwang.png"]
    return process_templates(templates, click_after_match=True)

def process_runtu():
    templates = ["runtu.png"]
    return process_templates(templates, click_after_match=True)

def process_cangying():
    templates = ["cangying.png"]
    return process_templates(templates, click_after_match=True)

def process_feilong():
    templates = ["feilong.png"]
    return process_templates(templates, click_after_match=True)

def process_leidian():
    templates = ["leidian.png"]
    return process_templates(templates, click_after_match=True)

def process_tianniao():
    templates = ["tianniao.png"]
    # 只返回坐标不自动点击
    return process_templates(templates, click_after_match=False)

def main_loop():
    """主循环逻辑"""
    for i in range(999):
        print(f"\n===== 主循环第 {i+1} 轮 =====")
        
        # 执行匹配操作
        process_pipei()
        
        #电鸟炮
        process_leidian()
        tianniao_result = process_tianniao()
        tianniao_coord = tianniao_result.get("tianniao.png")
        if tianniao_coord:
            for j in range(11):
                print(f"第 {j+1}/11 次点击tianniao")
                adb_click(*tianniao_coord)
                time.sleep(0.5)  # 每次点击间隔
        else:
            print("未找到tianniao，跳过点击")
            
        #下王
        process_nvhuang()
        adb_click(670,345)
        process_manwang()
        adb_click(670,345)
        process_yongwang()
        adb_click(670,345)
        process_runtu()
        adb_click(670,345)
        process_cangying()
        adb_click(670,345)

        
        # 循环点击操作
        for j in range(8):
            process_caoman()
            #process_feilong()
            inner_clicks = [
                (670, 345), (978, 170), (412, 584), (1519, 112),
                (1773, 304), (1833, 1091), (737, 1085)
            ]
            for x, y in inner_clicks:
                adb_click(x, y)
            print(f"第 {j+1}/8 次点击序列")
            time.sleep(0.5)
        
        # 延迟后执行回家操作
        time.sleep(30)
        process_huijia()
        time.sleep(5)


if __name__ == "__main__":
    main_loop()
    print("\n所有操作执行完毕")