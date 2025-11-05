# coc_autoclick
用python写的部落冲突自动化脚本

# 部落冲突自动化脚本

### 预先准备
请确保你已经安装了

装有部落冲突的网易mumu模拟器，分辨率为2560*1440

请确保你已经安装以下python库

opencv2

numpy

### 安装
1. **配置ADB**
找到网易mumu模拟器shell的地址，一般为D:\Program Files\Netease\MuMuPlayer-12.0\shell

在设置中找到环境变量，在系统变量中的Path下新建地址，把刚才的地址复制进去，一路确定

2. **设置模拟器**
在模拟器的设置中找到开发者选项，打开其下的“USB调试”

### 运行
1. **连接ADB**
终端输入adb connect 127.0.0.1:16384
2. **运行程序**
在项目目录中打开终端，然后输入python3 gui.py

设备中填入127.0.0.1:16384或者选择adb连接的设备


