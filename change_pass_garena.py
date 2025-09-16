import subprocess
import time
import sys
import os
import random
import string

# --- Configuration ---
LDPLAYER_ADB_ADDRESS = "localhost:5555"
# --- End Configuration ---

# Ensure UTF-8 output on Windows consoles
if os.name == 'nt':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except (AttributeError, ValueError):
        pass
    os.system('chcp 65001 >NUL')

def generate_password(length=9):
    """Tạo mật khẩu theo yêu cầu:
    - 1 chữ hoa (A-Z)
    - 1 số (0-9)
    - 1 ký tự đặc biệt (@#$%&)
    - Còn lại là chữ thường (a-z) hoặc ký tự đặc biệt (@#$%&)"""
    
    if length < 8 or length > 16:
        raise ValueError("Độ dài mật khẩu phải từ 8 đến 16 ký tự.")

    special_chars = "@#$%&"

    # Đảm bảo ít nhất 1 chữ hoa, 1 số, 1 ký tự đặc biệt
    upper = random.choice(string.ascii_uppercase)
    digit = random.choice(string.digits)
    special = random.choice(special_chars)

    # Các ký tự còn lại là chữ thường hoặc ký tự đặc biệt
    others = ''.join(random.choices(string.ascii_lowercase + special_chars, k=length - 3))

    # Trộn ngẫu nhiên
    password = list(upper + digit + special + others)
    random.shuffle(password)

    return ''.join(password)

def connect_to_device():
    """Tries to connect to the specified ADB address."""
    print(f"Đang kết nối tới LDPlayer tại {LDPLAYER_ADB_ADDRESS}...")
    subprocess.run(['adb', 'connect', LDPLAYER_ADB_ADDRESS], capture_output=True, text=True, shell=True)

def adb_command(cmd):
    """Executes an ADB command targeted at the specific device."""
    full_cmd = f"adb -s {LDPLAYER_ADB_ADDRESS} {cmd}"
    subprocess.run(full_cmd, shell=True)

def open_url_in_chrome(url):
    """Opens a specific URL in Google Chrome on the connected Android device."""
    command = f"shell am start -a android.intent.action.VIEW -d {url} com.android.chrome"
    print(f"Đang mở URL: {url}")
    adb_command(command)

def input_tap(x, y):
    """Simulates a tap action at a specific (x, y) coordinate."""
    command = f"shell input tap {x} {y}"
    print(f"Thực hiện nhấn vào tọa độ: ({x}, {y})")
    adb_command(command)

def input_text(text):
    """Simulates text input with escaping special characters."""
    # escape các ký tự đặc biệt trong shell
    special_chars = ['&', '|', ';', '<', '>', '(', ')', '$', '`', '\\', '"', "'", '!', '*', '?', '[', ']', '{', '}', '~']
    processed_text = ""
    for ch in text:
        if ch in special_chars:
            processed_text += "\\" + ch
        elif ch == " ":
            processed_text += "%s"   # adb dùng %s cho khoảng trắng
        else:
            processed_text += ch

    command = f"shell input text \"{processed_text}\""
    print(f"Nhập văn bản: {text}")
    adb_command(command)

def input_swipe(x1, y1, x2, y2, duration_ms=250):
    """Simulates a swipe gesture from (x1, y1) to (x2, y2) with duration in ms."""
    command = f"shell input swipe {x1} {y1} {x2} {y2} {duration_ms}"
    print(f"Vuốt từ ({x1}, {y1}) tới ({x2}, {y2}) trong {duration_ms}ms")
    adb_command(command)

def login_garena(username, password, username_coords, password_coords, login_button_coords):
    """Performs the Garena login."""
    print("--- Bắt đầu quá trình đăng nhập ---")
    input_tap(username_coords[0], username_coords[1])
    time.sleep(0.5)
    input_text(username)
    time.sleep(0.5)
    input_tap(password_coords[0], password_coords[1])
    time.sleep(0.5)
    input_text(password)
    time.sleep(0.5)
    input_tap(login_button_coords[0], login_button_coords[1])
    print("--- Hoàn tất đăng nhập ---")

def change_garena_password(username, password, current_password, new_password):
    """
    Main function to automate the entire password change process.
    The steps are hardcoded in this function.
    """
    print("=== BẮT ĐẦU QUÁ TRÌNH THAY ĐỔI MẬT KHẨU GARENA ===")

    # Steps are now defined directly in the code
    steps = [
        {
            "action": "navigate",
            "description": "Mở trang tài khoản Garena",
            "url": "https://account.garena.com/"
        },
        {
            "action": "login",
            "description": "Thực hiện đăng nhập",
            "delay": 1.5,
            "element": {
                "username_coords": [176, 318],
                "password_coords": [176, 390],
                "login_button_coords": [176, 600]
            }
        },
        {
            "action": "click",
            "description": "Nhấn vào mục 'Menu'",
            "delay": 1.5,
            "element": {
                "type": "coords",
                "coords": [32, 150]
            }
        },
        {
            "action": "click",
            "description": "Nhấn vào nút 'Bảo mật'",
            "element": {
                "type": "coords",
                "coords": [101, 327]
            }
        },
        {
            "action": "click",
            "description": "Nhấn vào nút 'Thay đổi'",
            "element": {
                "type": "coords",
                "coords": [462, 507]
            }
        },
        {
            "action": "click",
            "description": "Nhấn vào nút 'Thay đổi'",
            "element": {
                "type": "coords",
                "coords": [462, 507]
            }
        },
        {
            "action": "swipe",
            "description": "Vuốt lên nhẹ trước khi nhập mật khẩu",
            "element": {
                "type": "coords",
                "coords": [200, 800, 200, 400, 250]
            }
        },
        {
            "action": "swipe",
            "description": "Vuốt xuống nhẹ trước khi nhập mật khẩu",
            "element": {
                "type": "coords",
                "coords": [200, 400, 200, 800, 250]
            }
        },
        {
            "action": "input",
            "description": "Nhập mật khẩu hiện tại",
            "data": "current_password",
            "element": {
                "type": "coords",
                "coords": [42, 320]
            }
        },
        {
            "action": "input",
            "description": "Nhập mật khẩu mới",
            "data": "new_password",
            "element": {
                "type": "coords",
                "coords": [42, 410]
            }
        },
        {
            "action": "input",
            "description": "Xác nhận mật khẩu mới",
            "data": "confirm_new_password",
            "element": {
                "type": "coords",
                "coords": [45, 653]
            }
        },
        {
            "action": "click",
            "description": "Nhấn nút 'Áp dụng'",
            "element": {
                "type": "coords",
                "coords": [121, 739]
            }
        },
        {
            "action": "click",
            "description": "Nhấn vào nút 'avatar'",
            "element": {
                "type": "coords",
                "coords": [511, 149]
            }
        },
        {
            "action": "click",
            "description": "Nhấn vào nút 'Log out'",
            "element": {
                "type": "coords",
                "coords": [328, 901]
            }
        },
    ]

    # Connect to device
    connect_to_device()
    time.sleep(1)

    # Execute each step
    for step in steps:
        action = step.get('action')
        description = step.get('description')
        print(f"\nThực hiện bước: {description}")

        # Add a delay before each action
        time.sleep(step.get('delay', random.uniform(0.5, 1)))

        if action == 'navigate':
            open_url_in_chrome(step['url'])

        elif action == 'login':
            login_garena(
                username,
                password,
                step['element']['username_coords'],
                step['element']['password_coords'],
                step['element']['login_button_coords']
            )

        elif action == 'click':
            coords = step['element']['coords']
            input_tap(coords[0], coords[1])

        elif action == 'input':
            coords = step['element']['coords']
            data_key = step.get('data')
            text_to_input = ""
            if data_key == 'current_password':
                text_to_input = current_password
            elif data_key == 'new_password':
                text_to_input = new_password
            elif data_key == 'confirm_new_password':
                text_to_input = new_password
            
            if text_to_input:
                input_tap(coords[0], coords[1])
                time.sleep(0.5)
                input_text(text_to_input)
        elif action == 'swipe':
            coords = step['element']['coords']
            if len(coords) == 5:
                x1, y1, x2, y2, duration = coords
            else:
                x1, y1, x2, y2 = coords
                duration = 250
            input_swipe(x1, y1, x2, y2, duration)
        else:
            print(f"Hành động không xác định: {action}")

    print("\n=== HOÀN TẤT QUÁ TRÌNH THAY ĐỔI MẬT KHẨU ===")


if __name__ == "__main__":
    # --- THÔNG TIN CẦN THAY ĐỔI ---
    ACCOUNTS_FILE = "accounts.txt"
    # --- KẾT THÚC THÔNG TIN CẦN THAY ĐỔI ---

    if not os.path.exists(ACCOUNTS_FILE):
        print(f"Không tìm thấy file {ACCOUNTS_FILE}. Vui lòng tạo file với định dạng mỗi dòng: username|password")
        sys.exit(1)

    with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    accounts = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "|" not in line:
            print(f"Bỏ qua dòng không hợp lệ: {line}")
            continue
        username, password = [p.strip() for p in line.split("|", 1)]
        if not username or not password:
            print(f"Bỏ qua dòng thiếu thông tin: {line}")
            continue
        accounts.append((username, password))

    if not accounts:
        print("Không có tài khoản hợp lệ trong file.")
        sys.exit(1)

    for idx, (username, password) in enumerate(accounts, start=1):
        print(f"\n===== XỬ LÝ TÀI KHOẢN {idx}/{len(accounts)}: {username} =====")
        NEW_PASSWORD = generate_password()
        try:
            # password được dùng làm mật khẩu đăng nhập và mật khẩu hiện tại
            print(username, password, NEW_PASSWORD)
            change_garena_password(username, password, password, NEW_PASSWORD)
            print(f"\nThành công thông tin tài khoản là:\n{username}|{NEW_PASSWORD}|{password}")
            with open("output.txt", "a", encoding="utf-8") as out_f:
                out_f.write(f"{username}|{NEW_PASSWORD}|{password}\n")
        except KeyboardInterrupt:
            print("\nBị hủy bởi người dùng.")
            with open("error.txt", "a", encoding="utf-8") as out_f:
                out_f.write(f"{username}|{password}\n")
            sys.exit(130)
        except Exception as e:
            print(f"Lỗi khi xử lý tài khoản {username}: {e}")
            with open("error.txt", "a", encoding="utf-8") as out_f:
                out_f.write(f"{username}|{password}\n")
        # Nghỉ ngắn giữa các tài khoản để tránh bị chặn
        time.sleep(2)