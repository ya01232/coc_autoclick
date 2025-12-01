#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog
import subprocess
import sys
import threading
import os
import time
import re


class CocAutoLauncher:
    SCRIPTS = [
        {"id": 1, "name": "进攻脚本", "file": "jingong.py"},
        {"id": 2, "name": "奶号脚本", "file": "naihao.py"},
        {"id": 3, "name": "欢迎脚本", "file": "huanying.py"},
    ]

    def __init__(self, root):
        self.root = root
        self.root.title("部落冲突自动化脚本启动器")
        self.root.geometry("700x580")
        self.root.minsize(600, 500)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.running = False
        self.process = None
        self.current_script_id = None

        self.create_widgets()
        self.refresh_device_list()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 设备配置区域
        device_frame = ttk.LabelFrame(main_frame, text="设备配置", padding="10")
        device_frame.pack(fill=tk.X, pady=(0, 8))

        # 设备选择行
        row1 = ttk.Frame(device_frame)
        row1.pack(fill=tk.X, pady=3)
        ttk.Label(row1, text="设备地址:").pack(side=tk.LEFT)
        self.device_var = tk.StringVar()
        self.device_combobox = ttk.Combobox(
            row1,
            textvariable=self.device_var,
            width=35,
            state="readonly"
        )
        self.device_combobox.pack(side=tk.LEFT, padx=(5, 10))

        ttk.Button(row1, text="刷新列表", command=self.refresh_device_list, width=10).pack(side=tk.LEFT)
        ttk.Button(row1, text="连接设备", command=self.connect_specified_device, width=10).pack(side=tk.LEFT, padx=(5, 0))

        # 参数行
        row2 = ttk.Frame(device_frame)
        row2.pack(fill=tk.X, pady=5)
        ttk.Label(row2, text="匹配阈值:").pack(side=tk.LEFT)
        self.threshold_var = tk.StringVar(value="0.25")
        ttk.Entry(row2, textvariable=self.threshold_var, width=8).pack(side=tk.LEFT, padx=(5, 20))

        ttk.Label(row2, text="循环次数 (0=无限):").pack(side=tk.LEFT)
        self.loop_count_var = tk.StringVar(value="0")
        ttk.Entry(row2, textvariable=self.loop_count_var, width=6).pack(side=tk.LEFT, padx=(5, 0))

        # 脚本选择区域
        script_frame = ttk.LabelFrame(main_frame, text="脚本选择", padding="10")
        script_frame.pack(fill=tk.X, pady=(0, 8))

        self.script_var = tk.IntVar(value=1)
        for script in self.SCRIPTS:
            ttk.Radiobutton(
                script_frame,
                text=script["name"],
                variable=self.script_var,
                value=script["id"]
            ).pack(anchor=tk.W, pady=2)

        # 控制按钮
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 8))

        self.start_btn = ttk.Button(btn_frame, text="开始运行", command=self.start_script, width=12)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.stop_btn = ttk.Button(btn_frame, text="停止运行", command=self.stop_script, state=tk.DISABLED, width=12)
        self.stop_btn.pack(side=tk.LEFT)

        # 日志区域
        log_frame = ttk.LabelFrame(main_frame, text="运行日志", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True)

        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def log(self, message):
        timestamp = time.strftime("%H:%M:%S")
        line = f"[{timestamp}] {message}"

        def _insert():
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, line + "\n")
            self.log_text.see(tk.END)
            self.log_text.config(state=tk.DISABLED)

        if threading.current_thread() is threading.main_thread():
            _insert()
        else:
            self.root.after(10, _insert)

    def update_status(self, text):
        self.status_var.set(text)

    def refresh_device_list(self):
        self.log("正在刷新 ADB 设备列表...")
        self.update_status("正在刷新设备列表...")

        def _refresh():
            try:
                result = subprocess.run(
                    ["adb", "devices"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                devices = []
                for line in result.stdout.strip().splitlines()[1:]:
                    if line.strip() and "\tdevice" in line:
                        dev = line.split("\t")[0].strip()
                        devices.append(dev)

                self.root.after(0, lambda: self._update_device_list_ui(devices))
            except Exception as e:
                self.log(f"刷新设备失败: {e}")
                self.root.after(0, lambda: self.update_status("刷新失败"))

        threading.Thread(target=_refresh, daemon=True).start()

    def _update_device_list_ui(self, devices):
        self.device_combobox["values"] = devices
        if devices:
            if not self.device_var.get() or self.device_var.get() not in devices:
                self.device_var.set(devices[0])
            self.log(f"找到 {len(devices)} 个可用设备")
            self.update_status(f"已连接 {len(devices)} 个设备")
        else:
            self.log("未检测到任何 ADB 设备")
            self.update_status("无可用设备")

    def connect_specified_device(self):
        device = self.device_var.get().strip()
        if not device:
            device = simpledialog.askstring(
                "手动连接设备",
                "请输入 ADB 设备地址（如 127.0.0.1:5555）:",
                parent=self.root
            )
            if not device:
                return
            self.device_var.set(device)

        self.log(f"尝试连接设备: {device}")
        self.update_status(f"正在连接 {device}...")

        def _connect():
            try:
                result = subprocess.run(
                    ["adb", "connect", device],
                    capture_output=True,
                    text=True,
                    timeout=15
                )
                output = (result.stdout + result.stderr).strip()
                if "connected to" in output or "already connected" in output:
                    self.log(f"成功连接设备: {device}")
                    self.root.after(0, self.refresh_device_list)
                else:
                    self.log(f"连接失败: {output}")
            except Exception as e:
                self.log(f"连接异常: {e}")

        threading.Thread(target=_connect, daemon=True).start()

    def start_script(self):
        if self.running:
            messagebox.showinfo("提示", "脚本已在运行中，请先停止！", parent=self.root)
            return

        device = self.device_var.get().strip()
        if not device:
            messagebox.showerror("错误", "请先选择或连接一个设备！", parent=self.root)
            return

        try:
            threshold = float(self.threshold_var.get())
            if not (0.0 <= threshold <= 1.0):
                raise ValueError
        except ValueError:
            messagebox.showerror("参数错误", "匹配阈值必须是 0.0 ~ 1.0 之间的数字！", parent=self.root)
            return

        try:
            loop_count = int(self.loop_count_var.get())
            if loop_count < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("参数错误", "循环次数必须是非负整数！", parent=self.root)
            return

        script_id = self.script_var.get()
        selected_script = next((s for s in self.SCRIPTS if s["id"] == script_id), None)
        if not selected_script:
            messagebox.showerror("错误", "无效的脚本选择！", parent=self.root)
            return

        script_file = selected_script["file"]
        script_name = selected_script["name"]

        self.log(f"即将启动：{script_name}")
        self.log(f"设备: {device}")
        self.log(f"阈值: {threshold}")
        self.log(f"循环: {'无限' if loop_count == 0 else loop_count} 次")

        self.running = True
        self.current_script_id = script_id
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.update_status(f"{script_name} 运行中...")

        threading.Thread(
            target=self.run_script,
            args=(script_file, device, threshold, loop_count),
            daemon=True
        ).start()

    def run_script(self, script_file, device, threshold, loop_count):
        try:
            env = os.environ.copy()
            env["COC_DEVICE"] = device
            env["COC_THRESHOLD"] = str(threshold)
            env["COC_LOOP_COUNT"] = str(loop_count)

            self.log(f"启动进程: {sys.executable} {script_file}")

            self.process = subprocess.Popen(
                [sys.executable, script_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                env=env,
                bufsize=1,
                universal_newlines=True
            )

            for line in iter(self.process.stdout.readline, ''):
                if not self.running:
                    break
                clean_line = re.sub(r'\x1b$$[;?0-9]*[a-zA-Z]', '', line).strip()
                if clean_line:
                    self.log(f"[子进程] {clean_line}")

            self.process.wait()

            if self.running:
                code = self.process.returncode
                status = "正常结束" if code == 0 else f"异常退出（返回码: {code}）"
                self.log(f"脚本 {status}")

        except Exception as e:
            self.log(f"脚本运行崩溃: {e}")
        finally:
            self._cleanup_after_run()

    def _cleanup_after_run(self):
        self.running = False
        self.process = None
        self.current_script_id = None

        def _reset_ui():
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            script_name = {1: "进攻", 2: "奶号", 3: "欢迎"}.get(self.current_script_id, "脚本")
            self.update_status(f"{script_name}已结束")

        self.root.after(0, _reset_ui)

    def stop_script(self):
        if not self.running or not self.process:
            return

        self.log("正在请求停止脚本...")
        self.update_status("正在终止进程...")

        try:
            self.process.terminate()
            try:
                self.process.wait(timeout=3)
                self.log("进程已正常终止")
            except subprocess.TimeoutExpired:
                self.log("进程未响应，强制终止...")
                self.process.kill()
                self.process.wait(timeout=2)
                self.log("进程已强制终止")
        except Exception as e:
            self.log(f"终止失败: {e}")

        self._cleanup_after_run()

    def on_closing(self):
        if self.running:
            if messagebox.askokcancel("退出确认", "脚本正在运行中，确定要退出吗？\n（进程将被强制终止）", parent=self.root):
                self.stop_script()
                time.sleep(0.3)
                self.root.destroy()
        else:
            self.root.destroy()


if __name__ == "__main__":
    # Windows 高 DPI 适配（可选）
    if sys.platform == "win32":
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass

    root = tk.Tk()
    app = CocAutoLauncher(root)
    root.mainloop()