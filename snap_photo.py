#!/usr/bin/env python3
import os
import subprocess
from datetime import datetime
from pathlib import Path

SAVE_DIR = Path("/home/reyes")
SAVE_DIR.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
outfile = SAVE_DIR / f"photo_{timestamp}.jpg"

cmd = [
    "rpicam-still",
    "-n",                 # no preview (good for SSH/headless)
    "-t", "200",          # small warm-up time (ms)
    "-o", str(outfile),   # output file
]

try:
    subprocess.run(cmd, check=True)
    print(f"Saved: {outfile}")
except subprocess.CalledProcessError as e:
    print("Camera capture failed:", e)
