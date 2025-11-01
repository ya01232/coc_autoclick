import subprocess
import os

def adb_screenshot(save_path="screen.png", device="127.0.0.1:16384"):
    """
    通过ADB截取指定安卓设备屏幕并保存到本地指定路径
    
    参数:
        save_path: 本地保存截图的路径，默认值为"screen.png"
        device: 目标设备序列号，默认值为"127.0.0.1:16384"
    
    返回:
        截图在本地的保存路径
    """
    device_temp_path = "/sdcard/screen_temp.png"
    
    try:
        # 截取屏幕并保存到设备临时路径（指定设备）
        subprocess.run(
            f"adb -s {device} shell screencap -p {device_temp_path}",
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # 将设备上的临时截图拉取到本地（指定设备）
        subprocess.run(
            f"adb -s {device} pull {device_temp_path} {save_path}",
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        print(f"截图成功，保存路径：{os.path.abspath(save_path)}")
        
    finally:
        try:
            # 清理设备上的临时文件（指定设备）
            subprocess.run(
                f"adb -s {device} shell rm {device_temp_path}",
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        except:
            pass
    
    return save_path

if __name__ == "__main__":
    # 调用时可直接使用默认设备，也可通过参数指定其他设备
    adb_screenshot("screenshot.png")