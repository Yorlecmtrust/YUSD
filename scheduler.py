import subprocess
import time
import platform
import os
import sys

# ✅ Auto-install 'schedule' if missing
try:
    import schedule
except ImportError:
    print("📦 Installing required module: schedule")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "schedule"])
    import schedule

# === CONFIGURATION ===
START_TIME = "09:00"  # 9 AM
STOP_TIME = "11:00"   # 11 AM
WORKDAYS = ["monday", "wednesday", "friday"]
SCRIPT_PATH = "serverStablecoin.py"  # <-- Correct backend script

# Store the process handle
server_process = None

def start_server():
    global server_process
    if server_process is None:
        print("🟢 Starting FastAPI server...")
        server_process = subprocess.Popen(["uvicorn", SCRIPT_PATH.replace(".py", "") + ":app", "--host", "127.0.0.1", "--port", "8000"])
    else:
        print("⚠️ Server already running.")

def stop_server():
    global server_process
    if server_process is not None:
        print("🔴 Stopping FastAPI server...")
        server_process.terminate()
        server_process = None
    else:
        print("⚠️ Server not running.")

# Set scheduler for chosen weekdays
for day in WORKDAYS:
    getattr(schedule.every(), day).at(START_TIME).do(start_server)
    getattr(schedule.every(), day).at(STOP_TIME).do(stop_server)

print(f"⏰ Scheduler set: {START_TIME}–{STOP_TIME} on {', '.join(WORKDAYS).title()}s")
print("🔁 Running auto-scheduler loop...")

while True:
    schedule.run_pending()
    time.sleep(10)
