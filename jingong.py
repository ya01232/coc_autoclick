#!/usr/bin/env python3

import uiautomator2 as u2
import time
import subprocess
import sys
for i in range(10):
    subprocess.run([sys.executable, "screenshot.py"], check=True)
    subprocess.run([sys.executable, "pipei.py"], check=True)

    d=u2.connect("127.0.0.1:16384")
    d.swipe(900, 1800, 100, 200, 0.8)
    d.click(260, 1300)
    for i in range(10):
        d.click(670, 345)
        d.click(978, 170)
        d.click(412, 584)
        d.click(1519, 112)
        d.click(1773, 304)
        d.click(1833, 1091)
        d.click(737, 1085)
        print(f"第 {i+1}/50 次点击(860, 390)")
        time.sleep(0.5)

time.sleep(60)
d=u2.connect("127.0.0.1:16384")
d.click(186, 1070)
d.click(1546, 919)
d.click(1283, 1230)