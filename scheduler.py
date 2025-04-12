import schedule
import time
import platform
import subprocess
import os
from datetime import datetime

# === CONFIGURATION ===
SCRIPT_PATH = "serverStablecoin.py"
START_TIME = "09:00"
STOP_TIME = "11:00"
DAYS = ["monday", "wednesday", "friday"]

# === CONTROL LOGIC ===
def start_server():
    print(f"🟢 Starting {SCRIPT_PATH}")
    if platform.system() == "Windows":
        subprocess.Popen(["start", "cmd", "/k", f"python {SCRIPT_PATH}"], shell=True)
    else:
        subprocess.Popen(["python3", SCRIPT_PATH])

def stop_server():
    print(f"🔴 Stopping server...")
    if platform.system() == "Windows":
        os.system("taskkill /f /im python.exe")
    else:
        os.system("pkill -f serverStablecoin.py")

# === SCHEDULE SETUP ===
for day in DAYS:
    getattr(schedule.every(), day).at(START_TIME).do(start_server)
    getattr(schedule.every(), day).at(STOP_TIME).do(stop_server)

print(f"⏰ Scheduler set: {START_TIME}–{STOP_TIME} on {', '.join(DAYS).title()}s")
print("🔁 Running auto-scheduler loop...")

# === LOOP ===
while True:
    schedule.run_pending()
    time.sleep(1)
