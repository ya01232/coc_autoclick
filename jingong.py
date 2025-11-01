import uiautomator2 as u2
import time
import subprocess
import sys
import os
import cv2


# 全局变量存储当前模板的坐标
GLOBAL_X = None
GLOBAL_Y = None

def take_screenshot():
    """执行截图脚本并处理错误"""
    try:
        subprocess.run([sys.executable, "screenshot.py"], check=True)
        print("截图成功")
        # 截图后增加短暂延迟，确保文件写入完成
        time.sleep(0.5)
        return True
    except subprocess.CalledProcessError as e:
        print(f"截图失败：{e}")
        return False
    except FileNotFoundError:
        print("未找到screenshot.py脚本")
        return False

def get_xy(img_model_path, threshold=0.15, retry=2):
    """
    匹配模板并支持重试机制
    :param img_model_path: 模板路径
    :param threshold: 匹配阈值
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
    
    # 读取模板（只读取一次）
    img_model = cv2.imread(full_model_path)
    if img_model is None:
        print(f"无法读取模板：{full_model_path}")
        GLOBAL_X, GLOBAL_Y = None, None
        return None
    model_h, model_w = img_model.shape[:2]

    # 支持重试机制
    for attempt in range(retry + 1):
        # 读取原始图像（每次重试重新读，避免缓存）
        img = cv2.imread(img_path)
        if img is None:
            print(f"无法读取截图 {img_path}（尝试 {attempt + 1}/{retry + 1}）")
            time.sleep(0.5)
            continue

        # 模板匹配
        result = cv2.matchTemplate(img, img_model, cv2.TM_SQDIFF_NORMED)
        min_val, _, min_loc, _ = cv2.minMaxLoc(result)

        # 判断是否匹配成功
        if min_val <= threshold:
            GLOBAL_X = int(min_loc[0] + model_w / 2)
            GLOBAL_Y = int(min_loc[1] + model_h / 2)
            print(f"{img_model_path} 匹配成功（尝试 {attempt + 1}）：坐标 ({GLOBAL_X}, {GLOBAL_Y})，匹配值 {min_val:.4f}")
            return (GLOBAL_X, GLOBAL_Y)
        else:
            print(f"{img_model_path} 匹配失败（尝试 {attempt + 1}）：匹配值 {min_val:.4f} > 阈值 {threshold}")
            if attempt < retry:
                time.sleep(0.5)  # 重试前短暂等待

    # 所有重试都失败
    print(f"{img_model_path} 所有尝试均失败")
    GLOBAL_X, GLOBAL_Y = None, None
    return None


def process_templates(template_list, base_threshold=0.15, max_threshold=0.25, click_after_match=False):
    """
    依次处理模板，支持动态调整阈值
    :param template_list: 模板列表
    :param base_threshold: 基础阈值
    :param max_threshold: 最大允许阈值（动态调整上限）
    :param click_after_match: 是否点击
    :return: 结果字典
    """
    result_dict = {}
    d = u2.connect("127.0.0.1:16384")
    print("设备连接成功")
    
    for template in template_list:
        print(f"\n===== 处理模板：{template} =====")
        # 1. 截图
        if not take_screenshot():
            result_dict[template] = None
            continue
        
        # 2. 先尝试基础阈值，失败则逐步提高阈值重试（最多提高到max_threshold）
        current_threshold = base_threshold
        coord = None
        while current_threshold <= max_threshold:
            coord = get_xy(template, threshold=current_threshold, retry=1)
            if coord is not None:
                break  # 匹配成功则退出阈值调整循环
            # 每次失败提高0.02阈值（可根据需要调整）
            current_threshold += 0.02
            print(f" 提高阈值至 {current_threshold:.2f} 重试...")
        
        result_dict[template] = coord
        
        # 3. 点击（如果需要）
        if click_after_match and coord is not None:
            print(f"点击坐标：({GLOBAL_X}, {GLOBAL_Y})")
            d.click(GLOBAL_X, GLOBAL_Y)
            time.sleep(1.5)  # 延长等待时间，确保界面响应
        elif not coord:
            print(f" 跳过 {template} 点击（无有效坐标）")
    
    return result_dict


if __name__ == "__main__":
    templates_to_process = [
        "jingong.png",
        "sousuo.png",
        # 其他模板...
    ]
    
    results = process_templates(
        template_list=templates_to_process,
        base_threshold=0.15,    # 初始阈值
        max_threshold=0.25,     # 最大允许阈值（根据日志中失败的匹配值设置）
        click_after_match=True
    )
    
    print("\n 所有模板识别结果：")
    for name, coord in results.items():
        print(f"{name}: {coord}")

