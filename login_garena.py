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

def adb_command(cmd):
    """Executes an ADB command targeted at the specific device."""
    full_cmd = f"adb -s {LDPLAYER_ADB_ADDRESS} {cmd}"
    subprocess.run(full_cmd, shell=True)

def open_url_in_chrome(url):
    """
    Mở một URL cụ thể trong Google Chrome trên thiết bị Android được kết nối.
    """
    command = f"shell am start -a android.intent.action.VIEW -d {url} com.android.chrome"
    print(f"Đang thực thi lệnh: adb -s {LDPLAYER_ADB_ADDRESS} {command}")
    adb_command(command)

def input_tap(x, y):
    """
    Mô phỏng hành động nhấn (tap) vào một tọa độ (x, y) trên màn hình.
    """
    command = f"shell input tap {x} {y}"
    print(f"Thực hiện nhấn vào tọa độ: ({x}, {y})")
    adb_command(command)

def input_text(text):
    """
    Mô phỏng hành động nhập văn bản.
    Lưu ý: Văn bản không hỗ trợ ký tự đặc biệt hoặc khoảng trắng. 
    Để nhập khoảng trắng, sử dụng %s.
    """
    processed_text = text.replace(" ", "%s")
    command = f"shell input text {processed_text}"
    print(f"Nhập văn bản: {text}")
    adb_command(command)

def input_swipe(start_x, start_y, end_x, end_y, duration=250):
    """
    Mô phỏng hành động vuốt (swipe) trên màn hình.
    """
    swipe_command = f"shell input swipe {start_x} {start_y} {end_x} {end_y} {duration}"
    print(f"Thực hiện vuốt từ ({start_x}, {start_y}) đến ({end_x}, {end_y})")
    adb_command(swipe_command)

def login_garena(username, password, username_coords=(176, 318), password_coords=(176, 390), login_button_coords=(176, 600)):
    """
    Thực hiện đăng nhập Garena với thông tin được cung cấp.
    
    Args:
        username (str): Tên đăng nhập
        password (str): Mật khẩu
        username_coords (tuple): Tọa độ ô username (x, y)
        password_coords (tuple): Tọa độ ô password (x, y)
        login_button_coords (tuple): Tọa độ nút đăng nhập (x, y)
    """
    print(f"Bắt đầu quá trình đăng nhập với username: {username}")
    
    # 1. Nhấn vào ô Username
    print("1. Nhấn vào ô Username...")
    input_tap(username_coords[0], username_coords[1])
    time.sleep(0.5)
    
    # 2. Nhập username
    print("2. Nhập username...")
    input_text(username)
    time.sleep(0.5)
    
    # 3. Nhấn vào ô Password
    print("3. Nhấn vào ô Password...")
    input_tap(password_coords[0], password_coords[1])
    time.sleep(0.5)
    
    # 4. Nhập password
    print("4. Nhập password...")
    input_text(password)
    time.sleep(0.5)

    # 5. Vuốt lên để tránh bot
    print("5. Thực hiện vuốt lên để tránh bot...")
    input_swipe(200, 800, 200, 400, 250)
    time.sleep(0.5)

    # 6. Vuốt xuống để tránh bot
    print("6. Thực hiện vuốt xuống để tránh bot...")
    input_swipe(200, 400, 200, 800, 250)
    time.sleep(0.5)

    # 7. Nhấn nút Đăng nhập
    print("7. Nhấn nút Đăng nhập...")
    input_tap(login_button_coords[0], login_button_coords[1])
    
    print("✅ Hoàn tất quá trình đăng nhập!")

def auto_login_garena(username, password, garena_url="https://account.garena.com/"):
    """
    Tự động mở trang Garena và thực hiện đăng nhập.
    
    Args:
        username (str): Tên đăng nhập
        password (str): Mật khẩu
        garena_url (str): URL trang đăng nhập Garena
    """
    print("=== BẮT ĐẦU QUÁ TRÌNH ĐĂNG NHẬP GARENA ===")
    
    # Kết nối thiết bị
    connect_to_device()
    time.sleep(1)
    
    # Mở trang đăng nhập
    print(f"Mở trang đăng nhập Garena: {garena_url}")
    open_url_in_chrome(garena_url)
    time.sleep(2)  # Đợi trang web tải
    
    # Thực hiện đăng nhập
    login_garena(username, password)
    
    print("=== HOÀN TẤT QUÁ TRÌNH ĐĂNG NHẬP ===")

if __name__ == "__main__":
    # Ví dụ sử dụng các hàm mới
    
    # Cách 1: Sử dụng hàm auto_login_garena (đơn giản nhất)
    username = "Mio.x405"
    password = "0aks@hsmJ"
    auto_login_garena(username, password)
    
    # Cách 2: Sử dụng từng bước riêng lẻ (linh hoạt hơn)
    # connect_to_device()
    # time.sleep(1)
    # open_url_in_chrome("https://account.garena.com/")
    # time.sleep(3)
    # login_garena("Mio.x405", "0aks@hsmJ")
    
    # Cách 3: Tùy chỉnh tọa độ (nếu cần điều chỉnh)
    # custom_username_coords = (200, 300)  # Tọa độ mới cho username
    # custom_password_coords = (200, 400)  # Tọa độ mới cho password
    # custom_login_coords = (200, 500)     # Tọa độ mới cho nút đăng nhập
    # login_garena("Mio.x405", "0aks@hsmJ", 
    #              custom_username_coords, 
    #              custom_password_coords, 
    #              custom_login_coords)
