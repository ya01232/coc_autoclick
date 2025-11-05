import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import sys
import threading
import os
import time

class CocAutoClickGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("部落冲突自动化脚本")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # 确保中文显示正常
        self.style = ttk.Style()
        
        # 脚本运行状态
        self.running = False
        self.process = None
        
        # 创建界面组件
        self.create_widgets()
        
    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 设备配置区域
        device_frame = ttk.LabelFrame(main_frame, text="设备配置", padding="10")
        device_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(device_frame, text="设备地址:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.device_entry = ttk.Entry(device_frame, width=30)
        self.device_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
        self.device_entry.insert(0, "127.0.0.1:16384")  # 默认设备地址
        
        ttk.Label(device_frame, text="匹配阈值:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.threshold_entry = ttk.Entry(device_frame, width=10)
        self.threshold_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        self.threshold_entry.insert(0, "0.25")  # 默认阈值
        
        # 脚本选择区域
        script_frame = ttk.LabelFrame(main_frame, text="脚本选择", padding="10")
        script_frame.pack(fill=tk.X, pady=5)
        
        self.script_var = tk.IntVar(value=1)
        ttk.Radiobutton(script_frame, text="进攻脚本", variable=self.script_var, value=1).pack(anchor=tk.W, pady=2)
        ttk.Radiobutton(script_frame, text="匹配脚本", variable=self.script_var, value=2).pack(anchor=tk.W, pady=2)
        
        # 操作按钮区域
        btn_frame = ttk.Frame(main_frame, padding="10")
        btn_frame.pack(fill=tk.X, pady=5)
        
        self.start_btn = ttk.Button(btn_frame, text="开始运行", command=self.start_script)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(btn_frame, text="停止运行", command=self.stop_script, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        self.adb_connect_btn = ttk.Button(btn_frame, text="连接设备", command=self.connect_device)
        self.adb_connect_btn.pack(side=tk.LEFT, padx=5)
        
        # 日志显示区域
        log_frame = ttk.LabelFrame(main_frame, text="运行日志", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=15)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(state=tk.DISABLED)
        
        # 状态条
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def log(self, message):
        """添加日志信息"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        
    def update_status(self, status):
        """更新状态条"""
        self.status_var.set(status)
        
    def connect_device(self):
        """连接ADB设备"""
        device = self.device_entry.get().strip()
        if not device:
            messagebox.showerror("错误", "请输入设备地址")
            return
            
        self.log(f"尝试连接设备: {device}")
        self.update_status("正在连接设备...")
        
        try:
            # 执行ADB连接命令
            result = subprocess.run(
                ["adb", "connect", device],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if "connected to" in result.stdout:
                self.log(f"设备连接成功: {device}")
                self.log("正在初始化uiautomator2...")
                
                # 初始化uiautomator2
                init_result = subprocess.run(
                    [sys.executable, "-m", "uiautomator2", "init"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if init_result.returncode == 0:
                    self.log("uiautomator2初始化成功")
                    self.log("请确认模拟器中已出现ATX应用")
                    self.update_status("设备已连接")
                else:
                    self.log(f"uiautomator2初始化失败: {init_result.stderr}")
                    self.update_status("初始化失败")
            else:
                self.log(f"设备连接失败: {result.stderr}")
                self.update_status("连接失败")
                
        except Exception as e:
            self.log(f"连接设备时出错: {str(e)}")
            self.update_status("连接出错")
    
    def start_script(self):
        """启动选中的脚本"""
        if self.running:
            messagebox.showinfo("提示", "脚本已在运行中")
            return
            
        script_id = self.script_var.get()
        device = self.device_entry.get().strip()
        threshold = self.threshold_entry.get().strip()
        
        # 验证输入
        if not device:
            messagebox.showerror("错误", "请输入设备地址")
            return
            
        try:
            float(threshold)
        except ValueError:
            messagebox.showerror("错误", "请输入有效的匹配阈值")
            return
            
        # 确定要运行的脚本
        script_file = "jingong.py" if script_id == 1 else "1.py"
        
        # 检查脚本文件是否存在
        if not os.path.exists(script_file):
            messagebox.showerror("错误", f"未找到脚本文件: {script_file}")
            return
            
        self.log(f"开始运行{'进攻' if script_id == 1 else '匹配'}脚本...")
        self.log(f"设备: {device}, 阈值: {threshold}")
        
        # 更新UI状态
        self.running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.update_status("脚本运行中...")
        
        # 在新线程中运行脚本，避免UI卡死
        threading.Thread(
            target=self.run_script,
            args=(script_file, device, threshold),
            daemon=True
        ).start()
    
    def run_script(self, script_file, device, threshold):
        """运行脚本的实际方法"""
        try:
            # 设置环境变量，传递设备和阈值参数
            env = os.environ.copy()
            env["COC_DEVICE"] = device
            env["COC_THRESHOLD"] = threshold
            
            # 启动脚本进程
            self.process = subprocess.Popen(
                [sys.executable, script_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                env=env
            )
            
            # 实时读取输出并显示到日志
            for line in self.process.stdout:
                if not self.running:
                    break
                self.log(line.strip())
                
            # 等待进程结束
            self.process.wait()
            
            if self.running:  # 如果不是被手动停止的
                self.log(f"脚本运行结束，返回代码: {self.process.returncode}")
                self.update_status("脚本已结束")
                
        except Exception as e:
            self.log(f"脚本运行出错: {str(e)}")
            self.update_status("运行出错")
            
        finally:
            # 重置状态
            self.running = False
            self.process = None
            self.root.after(0, lambda: self.start_btn.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.stop_btn.config(state=tk.DISABLED))
    
    def stop_script(self):
        """停止正在运行的脚本"""
        if not self.running or not self.process:
            return
            
        self.log("正在停止脚本...")
        self.update_status("正在停止...")
        
        try:
            # 终止进程
            self.process.terminate()
            # 等待进程结束
            self.process.wait(timeout=5)
            self.log("脚本已停止")
            self.update_status("已停止")
        except subprocess.TimeoutExpired:
            # 强制杀死进程
            self.process.kill()
            self.log("脚本已强制停止")
            self.update_status("已强制停止")
        except Exception as e:
            self.log(f"停止脚本时出错: {str(e)}")
            self.update_status("停止出错")
            
        # 重置状态
        self.running = False
        self.process = None
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = CocAutoClickGUI(root)
    root.mainloop()