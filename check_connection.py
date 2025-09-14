import subprocess
import os
import sys

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
    # Use shell=True for safety on Windows with complex commands
    subprocess.run(['adb', 'connect', LDPLAYER_ADB_ADDRESS], capture_output=True, text=True, shell=True)

def check_device_connection():
    """
    Sử dụng lệnh 'adb devices' để kiểm tra các thiết bị đang kết nối.
    """
    connect_to_device()
    
    print("Đang kiểm tra kết nối với LDPlayer...")
    
    # Chạy lệnh 'adb devices' và lấy kết quả trả về
    # 'capture_output=True' và 'text=True' để lấy kết quả dạng chuỗi
    result = subprocess.run(['adb', 'devices'], capture_output=True, text=True, shell=True)
    
    # In kết quả ra màn hình
    print("\n--- Kết quả từ ADB ---")
    print(result.stdout)
    print("----------------------\n")
    
    # Phân tích kết quả
    if LDPLAYER_ADB_ADDRESS in result.stdout:
        print(f"✅ Thành công! Đã tìm thấy LDPlayer tại {LDPLAYER_ADB_ADDRESS}.")
    else:
        print("❌ Thất bại! Không tìm thấy LDPlayer.")
        print("Gợi ý: Hãy chắc chắn rằng LDPlayer đang chạy và bạn đã bật USB Debugging.")

if __name__ == "__main__":
    check_device_connection()
