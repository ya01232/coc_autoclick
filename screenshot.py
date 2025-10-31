import subprocess
import os

def adb_screenshot(save_path="screen.png"):
    """
    通过ADB截取安卓设备屏幕并保存到本地指定路径
    
    参数:
        save_path: 本地保存截图的路径，默认值为"screen.png"
    
    返回:
        截图在本地的保存路径
    """
    device_temp_path = "/sdcard/screen_temp.png"
    
    try:
        subprocess.run(
            f"adb shell screencap -p {device_temp_path}",
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        subprocess.run(
            f"adb pull {device_temp_path} {save_path}",
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        print(f"截图成功，保存路径：{os.path.abspath(save_path)}")
        
    finally:
        try:
            subprocess.run(
                f"adb shell rm {device_temp_path}",
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        except:
            pass
    
    return save_path

if __name__ == "__main__":
    adb_screenshot("screenshot.png")