# coc_autoclick
用python写的部落冲突自动化脚本

# 部落冲突自动化脚本

### 预先准备
请确保你已经安装了

装有部落冲突的网易mumu模拟器，分辨率为2560*1440

请确保你已经安装以下python库

uiautomator2

opencv2

numpy

### 安装
1. **配置ADB**
找到网易mumu模拟器shell的地址，一般为D:\Program Files\Netease\MuMuPlayer-12.0\shell

在设置中找到环境变量，在系统变量中的Path下新建地址，把刚才的地址复制进去，一路确定

2. **设置模拟器**
在模拟器的设置中找到开发者选项，打开其下的“USB调试”

3. **初始化uiautomator2**
在cmd中输入adb connect 127.0.0.1:16384

然后输入python -m uiautomator2 init

等待运行，如果在模拟器中看到名为“ATX”的图标为小车的应用，则初始化完成
