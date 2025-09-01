import subprocess
import os
import sys

# Ensure UTF-8 output on Windows consoles to avoid UnicodeEncodeError
if os.name == 'nt':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except (AttributeError, ValueError):
        pass
    os.system('chcp 65001 >NUL')

def check_device_connection():
    """
    Sử dụng lệnh 'adb devices' để kiểm tra các thiết bị đang kết nối.
    """
    print("Đang kiểm tra kết nối với LDPlayer...")
    
    # Chạy lệnh 'adb devices' và lấy kết quả trả về
    # 'capture_output=True' và 'text=True' để lấy kết quả dạng chuỗi
    result = subprocess.run(['adb', 'devices'], capture_output=True, text=True, shell=True)
    
    # In kết quả ra màn hình
    print("\n--- Kết quả từ ADB ---")
    print(result.stdout)
    print("----------------------\n")
    
    # Phân tích kết quả
    if "emulator" in result.stdout or "127.0.0.1" in result.stdout:
        print("✅ Thành công! Đã tìm thấy LDPlayer.")
    else:
        print("❌ Thất bại! Không tìm thấy LDPlayer.")
        print("Gợi ý: Hãy chắc chắn rằng LDPlayer đang chạy và bạn đã bật USB Debugging.")

if __name__ == "__main__":
    check_device_connection()