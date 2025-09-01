import subprocess
import time
import sys
import os

# Ensure UTF-8 output on Windows consoles to avoid UnicodeEncodeError
if os.name == 'nt':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except (AttributeError, ValueError):
        pass
    os.system('chcp 65001 >NUL')

def open_app(package_name, activity_name):
    """
    Mở một ứng dụng cụ thể bằng package và activity name.
    """
    command = f"adb shell am start -n {package_name}/{activity_name}"
    print(f"Đang thực thi lệnh: {command}")
    
    # shell=True cần thiết cho các lệnh phức tạp trên Windows
    subprocess.run(command, shell=True)

if __name__ == "__main__":
    # Package và activity name của Google Chrome trên Android
    chrome_package = "com.android.chrome"
    chrome_activity = "com.google.android.apps.chrome.Main"
    
    print("Chuẩn bị mở Google Chrome trong 3 giây...")
    time.sleep(3)
    open_app(chrome_package, chrome_activity)
    print("✅ Đã gửi lệnh mở Google Chrome!")


