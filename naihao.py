import os
import subprocess



DEVICE = os.getenv("COC_DEVICE", "127.0.0.1:16384")
subprocess.run(["adb", "connect", DEVICE])
