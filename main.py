#!/usr/bin/env python3

import subprocess
import sys


a=input("选择脚本：...1-进攻 2-匹配")

if a=="1":
    subprocess.run([sys.executable, "jingong.py"], check=True)
elif a=="2":
    subprocess.run([sys.executable, "pipei.py"], check=True)
else:
    print("无效选择")
