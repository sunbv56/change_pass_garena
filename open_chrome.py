import subprocess
import time
import sys
import os

# --- Configuration ---
LDPLAYER_ADB_ADDRESS = "localhost:5555"
# --- End Configuration ---

# Ensure UTF-8 output on Windows consoles to avoid UnicodeEncodeError
if os.name == 'nt':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except (AttributeError, ValueError):
        pass
    os.system('chcp 65001 >NUL')

def connect_to_device():
    """Tries to connect to the specified ADB address."""
    print(f"Đang kết nối tới LDPlayer tại {LDPLAYER_ADB_ADDRESS}...")
    subprocess.run(['adb', 'connect', LDPLAYER_ADB_ADDRESS], capture_output=True, text=True, shell=True)

def open_app(package_name, activity_name):
    """
    Mở một ứng dụng cụ thể bằng package và activity name.
    """
    # Command now specifies the device address
    command = f"adb -s {LDPLAYER_ADB_ADDRESS} shell am start -n {package_name}/{activity_name}"
    print(f"Đang thực thi lệnh: {command}")
    
    # shell=True cần thiết cho các lệnh phức tạp trên Windows
    subprocess.run(command, shell=True)

if __name__ == "__main__":
    # First, ensure we are connected
    connect_to_device()
    time.sleep(1) # Pause briefly to ensure connection is established

    # Package và activity name của Google Chrome trên Android
    chrome_package = "com.android.chrome"
    chrome_activity = "com.google.android.apps.chrome.Main"
    
    print("Chuẩn bị mở Google Chrome trong 3 giây...")
    time.sleep(3)
    open_app(chrome_package, chrome_activity)
    print("✅ Đã gửi lệnh mở Google Chrome!")


