import customtkinter
import threading
import queue
import os
import sys
import time
import subprocess
import random
import string
import re
import requests

# --- Configuration ---
LDPLAYER_ADB_ADDRESS = "localhost:5555"
ACCOUNTS_FILE = "accounts.txt"
OUTPUT_FILE = "output.txt"
ERROR_FILE = "error.txt"
PROXY_FILE = "proxies.txt"
CHROME_PACKAGE_NAME = "com.android.chrome"
CHROME_MAIN_ACTIVITY = "com.google.android.apps.chrome.Main"
API_KEY_KiotProxy = "Kbac764a3207e4410bbe66904b964ec13"
first_Proxy = True # true: lấy proxy mới, false: lấy proxy hiện tại
# --- End Configuration ---

# ===================================================================================
# == CORE AUTOMATION LOGIC (from change_pass_garena.py & close_chrome_tabs.py) ==
# ===================================================================================

def generate_password(length=9):
    """Tạo mật khẩu theo yêu cầu: 1 chữ hoa, 1 số, 1 ký tự đặc biệt."""
    if length < 8 or length > 16:
        raise ValueError("Độ dài mật khẩu phải từ 8 đến 16 ký tự.")
    special_chars = "@#$&"
    upper = random.choice(string.ascii_uppercase)
    digit = random.choice(string.digits)
    special = random.choice(special_chars)
    others = ''.join(random.choices(string.ascii_lowercase + special_chars, k=length - 3))
    password_list = list(upper + digit + special + others)
    random.shuffle(password_list)
    return ''.join(password_list)

def run_adb_command(command, timeout=15):
    """Runs a complete ADB command and returns its output."""
    full_command = f"adb -s {LDPLAYER_ADB_ADDRESS} {command}"
    try:
        result = subprocess.run(
            full_command,
            shell=True,
            capture_output=True,
            text=True,
            check=True,
            timeout=timeout,
            encoding='utf-8',
            errors='ignore'
        )
        return result.stdout.strip(), result.stderr.strip()
    except FileNotFoundError:
        return None, "Lỗi: Không tìm thấy lệnh 'adb'. Vui lòng cài đặt Android SDK Platform-Tools và thêm vào PATH."
    except subprocess.CalledProcessError as e:
        return e.stdout.strip(), e.stderr.strip()
    except subprocess.TimeoutExpired:
        return None, f"Lệnh ADB hết thời gian chờ: {full_command}"

def connect_to_device(logger=print):
    """Tries to connect to the specified ADB address."""
    logger(f"Đang kết nối tới LDPlayer tại {LDPLAYER_ADB_ADDRESS}...")
    connect_command = f"adb connect {LDPLAYER_ADB_ADDRESS}"
    subprocess.run(connect_command, shell=True, capture_output=True)
    time.sleep(1)
    result = subprocess.run("adb devices", shell=True, capture_output=True, text=True)
    if LDPLAYER_ADB_ADDRESS in result.stdout:
        logger(f"✓ Kết nối thành công tới {LDPLAYER_ADB_ADDRESS}.")
        return True
    else:
        logger(f"✗ Lỗi: Không thể kết nối tới LDPlayer tại {LDPLAYER_ADB_ADDRESS}.")
        logger("   Vui lòng đảm bảo LDPlayer đang chạy và đã bật ADB/USB Debugging.")
        return False

def adb_command(cmd, logger=print):
    """Executes an ADB command targeted at the specific device."""
    full_cmd = f"adb -s {LDPLAYER_ADB_ADDRESS} {cmd}"
    subprocess.run(full_cmd, shell=True, capture_output=True) # Hide output from console

def adb_capture(cmd, logger=print):
    """Executes an ADB command and captures stdout as text."""
    full_cmd = f"adb -s {LDPLAYER_ADB_ADDRESS} {cmd}"
    result = subprocess.run(full_cmd, capture_output=True, text=True, shell=True)
    return result.stdout or ""

def dump_ui_xml(logger=print):
    """Dumps current UI hierarchy to XML on device and returns its content."""
    adb_command("shell uiautomator dump /sdcard/window_dump.xml", logger)
    return adb_capture("shell cat /sdcard/window_dump.xml", logger)

def extract_text_from_ui_xml(xml_content):
    """Extracts visible text/content-desc values from UIAutomator XML."""
    if not xml_content: return ""
    texts = re.findall(r'text="([^"]+)"', xml_content)
    texts.extend(re.findall(r'content-desc="([^"]+)"', xml_content))
    return "\n".join(t.strip() for t in texts if t and t.strip())

def check_any_keyword_present(keywords, stop_event, logger=print, retries=10, interval_seconds=0.5, context_label=""):
    """Polls the current screen for any of the given keywords."""
    normalized_keywords = [k.strip().lower() for k in keywords if k and k.strip()]
    for attempt in range(1, retries + 1):
        if stop_event.is_set(): return False
        xml = dump_ui_xml(logger)
        haystack = (extract_text_from_ui_xml(xml) or xml or "").lower()
        if any(k in haystack for k in normalized_keywords):
            logger(f"✓ Phát hiện từ khóa thành công ({context_label}).")
            return True
        logger(f"   Chưa thấy từ khóa ({context_label}). Thử lại {attempt}/{retries}...")
        time.sleep(interval_seconds)
    return False

def open_url_in_chrome(url, logger=print):
    """Opens a specific URL in Google Chrome on the connected Android device."""
    command = f"shell am start -a android.intent.action.VIEW -d {url} com.android.chrome"
    logger(f"Đang mở URL: {url}")
    adb_command(command, logger)

def input_tap(x, y, logger=print):
    """Simulates a tap action at a specific (x, y) coordinate."""
    command = f"shell input tap {x} {y}"
    logger(f"   Nhấn vào tọa độ: ({x}, {y})")
    adb_command(command, logger)

def input_text(text: str, logger=print):
    """Simulates text input using ADB."""
    special_chars = [
        '&', '|', ';', '<', '>', '(', ')', '$', '`', '\\',
        '"', "'", '!', '*', '?', '[', ']', '{', '}', '~', '#'
    ]

    processed_text = ""
    for ch in text:
        if ch == " ":
            processed_text += "%s"
        # elif ch == "@":
        #     processed_text += "%40"
        # elif ch == "%":
        #     processed_text += "%25"
        elif ch in special_chars:
            processed_text += "\\" + ch
        else:
            processed_text += ch

    command = f"shell input text \"{processed_text}\""
    logger(f"   Nhập văn bản: {text}")
    adb_command(command, logger)

def input_swipe(x1, y1, x2, y2, duration_ms=250, logger=print):
    """Simulates a swipe gesture."""
    command = f"shell input swipe {x1} {y1} {x2} {y2} {duration_ms}"
    logger(f"   Vuốt từ ({x1}, {y1}) tới ({x2}, {y2})")
    adb_command(command, logger)

def close_all_chrome_tabs(logger=print):
    """Closes all Chrome tabs by performing a series of clicks."""
    logger("--- Bắt đầu đóng các tab Chrome ---")
    if not connect_to_device(logger):
        return

    start_command = f"shell am start -n {CHROME_PACKAGE_NAME}/{CHROME_MAIN_ACTIVITY}"
    run_adb_command(start_command)
    time.sleep(2)

    click_coordinates = [(431, 77), (503, 79), (313, 369), (118, 213), (137, 575), (404, 860), (43, 80)]
    for i, (x, y) in enumerate(click_coordinates, 1):
        logger(f"   Thực hiện nhấn lần {i}/{len(click_coordinates)} tại ({x}, {y}) để đóng tab.")
        click_command = f"shell input tap {x} {y}"
        run_adb_command(click_command)
        time.sleep(0.5)
    logger("--- Đã đóng các tab Chrome ---")

def delete_proxy_via_adb(logger=print):
    """Xóa proxy hệ thống qua ADB."""
    commands = [
        "shell settings delete global http_proxy",
        # "shell settings delete system http_proxy",
    ]
    for cmd in commands:
        run_adb_command(cmd)

def apply_proxy_via_adb(proxy: str, logger=print):
    """Áp dụng proxy (http) ở mức hệ thống qua ADB. Định dạng proxy: host:port"""
    if not proxy or ":" not in proxy:
        logger("✗ Proxy không hợp lệ. Yêu cầu định dạng host:port")
        return
    host, port = proxy.split(":", 1)
    host, port = host.strip(), port.strip()
    if not host or not port.isdigit():
        logger("✗ Proxy không hợp lệ. Yêu cầu định dạng host:port với port là số")
        return

    logger(f"Đang đặt proxy hệ thống: {host}:{port}")
    # Một số thiết bị dùng các key khác nhau, thiết lập nhiều key để tăng tương thích
    commands = [
        f"shell settings put global http_proxy {host}:{port}",
        # f"shell settings put system http_proxy {host}:{port}",
        # f"shell settings put global global_http_proxy_host {host}",
        # f"shell settings put global global_http_proxy_port {port}",
        # "shell settings delete global http_proxy_pac",
        # "shell settings delete system http_proxy_pac",
    ]
    for cmd in commands:
        run_adb_command(cmd)

    # Khởi động lại Chrome để nhận cấu hình mới
    logger("Khởi động lại Chrome để áp dụng proxy mới...")
    run_adb_command(f"shell am force-stop {CHROME_PACKAGE_NAME}")
    time.sleep(1)
    run_adb_command(f"shell monkey -p {CHROME_PACKAGE_NAME} -c android.intent.category.LAUNCHER 1")
    time.sleep(1)

def get_current_proxy(api_key: str):
    """
    Lấy proxy mới từ KiotProxy
    :param api_key: Key của bạn (string)
    :return: dict chứa thông tin proxy hoặc None nếu thất bại
    """
    url = "https://api.kiotproxy.com/api/v1/proxies/current"
    params = {
        "key": api_key
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if data.get("success"):
            proxy_data = data["data"]
            print("✅ Proxy mới nhận được:")
            print(f"  - HTTP:  {proxy_data['http']}")
            print(f"  - SOCKS5: {proxy_data['socks5']}")
            print(f"  - IP: {proxy_data['realIpAddress']} ({proxy_data['location']})")
            print(f"  - TTL: {proxy_data['ttl']} giây")
            return proxy_data
        else:
            print("❌ Thất bại:", data.get("message"))
            return None

    except Exception as e:
        print("Lỗi khi gọi API:", e)
        return None

def get_new_proxy(api_key: str, region: str = "random"):
    """
    Lấy proxy mới từ KiotProxy
    :param api_key: Key của bạn (string)
    :param region: Vùng proxy ('bac', 'trung', 'nam', 'random')
    :return: dict chứa thông tin proxy hoặc None nếu thất bại
    """
    url = "https://api.kiotproxy.com/api/v1/proxies/new"
    params = {
        "key": api_key,
        "region": region
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if data.get("success"):
            proxy_data = data["data"]
            print("✅ Proxy mới nhận được:")
            print(f"  - HTTP:  {proxy_data['http']}")
            print(f"  - SOCKS5: {proxy_data['socks5']}")
            print(f"  - IP: {proxy_data['realIpAddress']} ({proxy_data['location']})")
            print(f"  - TTL: {proxy_data['ttl']} giây")
            return proxy_data
        else:
            print("❌ Thất bại:", data.get("message"))
            print("=> Trả về proxy hiện tại!")
            return get_current_proxy(api_key)

    except Exception as e:
        print("Lỗi khi gọi API:", e)
        return None

def change_garena_password(username, password, new_password, stop_event, logger=print):
    """Main function to automate the entire password change process."""
    logger("=== BẮT ĐẦU QUÁ TRÌNH THAY ĐỔI MẬT KHẨU GARENA ===")

    steps = [
        {"action": "navigate", "description": "Mở trang tài khoản Garena", "url": "https://account.garena.com/"},
        {"action": "login", "description": "Thực hiện đăng nhập", "delay": 3, "element": {"username_coords": [176, 318], "password_coords": [176, 390], "login_button_coords": [176, 600]}},
        {"action": "check", "description": "Kiểm tra đăng nhập thành công", "check_type": "login_success", "retries": 6, "interval": 0.5},
        {"action": "click", "description": "Nhấn vào mục 'Menu'", "delay": 1.5, "element": {"coords": [32, 150]}},
        {"action": "click", "description": "Nhấn vào nút 'Bảo mật'", "element": {"coords": [101, 327]}},
        {"action": "click", "description": "Nhấn vào nút 'Thay đổi'", "element": {"coords": [462, 507]}},
        {"action": "click", "description": "Nhấn vào nút 'Thay đổi' (lần 2)", "element": {"coords": [462, 507]}},
        {"action": "swipe", "description": "Vuốt lên", "element": {"coords": [200, 800, 200, 400, 250]}},
        {"action": "swipe", "description": "Vuốt xuống", "element": {"coords": [200, 400, 200, 800, 250]}},
        {"action": "input", "description": "Nhập mật khẩu hiện tại", "data": "current_password", "element": {"coords": [42, 320]}},
        {"action": "input", "description": "Nhập mật khẩu mới", "data": "new_password", "element": {"coords": [42, 410]}},
        {"action": "input", "description": "Xác nhận mật khẩu mới", "data": "confirm_new_password", "element": {"coords": [45, 653]}},
        {"action": "click", "description": "Nhấn nút 'Áp dụng'", "element": {"coords": [121, 739]}},
        {"action": "check", "description": "Kiểm tra đổi mật khẩu thành công", "check_type": "change_success", "retries": 6, "interval": 0.5},
        {"action": "click", "description": "Nhấn vào nút 'avatar'", "element": {"coords": [511, 149]}},
        {"action": "click", "description": "Nhấn vào nút 'Log out'", "element": {"coords": [328, 901]}},
    ]

    for step in steps:
        if stop_event.is_set():
            logger("! Quá trình bị dừng bởi người dùng.")
            raise InterruptedError("Process stopped by user")

        action, description = step.get('action'), step.get('description')
        logger(f"-> {description}")
        time.sleep(step.get('delay', random.uniform(0.5, 1)))

        if action == 'navigate':
            open_url_in_chrome(step['url'], logger)
        elif action == 'login':
            elem = step['element']
            input_tap(elem['username_coords'][0], elem['username_coords'][1], logger)
            time.sleep(0.5)
            input_text(username, logger)
            time.sleep(0.5)
            input_tap(elem['password_coords'][0], elem['password_coords'][1], logger)
            time.sleep(0.5)
            input_text(password, logger)
            time.sleep(0.5)
            value_swipe = [200, 800, 200, 400, 250]
            input_swipe(*value_swipe, logger=logger)
            time.sleep(0.5)
            value_swipe = [200, 400, 200, 800, 250]
            input_swipe(*value_swipe, logger=logger)
            time.sleep(0.5)
            input_tap(elem['login_button_coords'][0], elem['login_button_coords'][1], logger)
        elif action == 'click':
            coords = step['element']['coords']
            input_tap(coords[0], coords[1], logger)
        elif action == 'input':
            coords = step['element']['coords']
            data_key = step.get('data')
            text_to_input = {"current_password": password, "new_password": new_password, "confirm_new_password": new_password}.get(data_key)
            if text_to_input:
                input_tap(coords[0], coords[1], logger)
                time.sleep(0.5)
                input_text(text_to_input, logger)
        elif action == 'swipe':
            coords = step['element']['coords']
            input_swipe(*coords, logger=logger)
        elif action == 'check':
            check_type = step.get('check_type')
            retries, interval = step.get('retries', 15), step.get('interval', 1.0)
            keywords, context, error_msg = (
                (["SECURITY LEVEL", "SENSITIVE OPERATION", "LOG IN HISTORY", "MỨC ĐỘ BẢO MẬT", "HOẠT ĐỘNG TÀI KHOẢN", "LỊCH SỬ ĐĂNG NHẬP"], "login", "LoiDangNhap")
                if check_type == 'login_success' else
                (["account.garena.com/security/password/done"], "change_password", "LoiDoiMatKhau")
            )
            if not check_any_keyword_present(keywords, stop_event, logger, retries, interval, context):
                # Thực hiện logout trước khi raise LoiDoiMatKhau
                if check_type == 'change_success':
                    input_tap(511, 149, logger)  # Click avatar
                    time.sleep(1)
                    input_tap(328, 901, logger)  # Click logout
                    time.sleep(1)
                raise RuntimeError(error_msg)

        if stop_event.is_set():
            logger("! Quá trình bị dừng bởi người dùng.")
            raise InterruptedError("Process stopped by user")

    logger("✓ HOÀN TẤT QUÁ TRÌNH THAY ĐỔI MẬT KHẨU")

# ===================================================================================
# ======================== GUI APPLICATION (from app.py) ==========================
# ===================================================================================

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("Garena Password Changer Tool")
        self.geometry("700x500")
        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("blue")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.controls_frame = customtkinter.CTkFrame(self)
        self.controls_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.start_button = customtkinter.CTkButton(self.controls_frame, text="Bắt đầu", command=self.start_processing)
        self.start_button.pack(side="left", padx=5, pady=5)

        self.stop_button = customtkinter.CTkButton(self.controls_frame, text="Dừng", command=self.stop_processing, state="disabled")
        self.stop_button.pack(side="left", padx=5, pady=5)

        self.close_tabs_button = customtkinter.CTkButton(self.controls_frame, text="Dọn dẹp Chrome", command=self.manual_close_chrome_tabs)
        self.close_tabs_button.pack(side="left", padx=5, pady=5)

        self.log_textbox = customtkinter.CTkTextbox(self, state="disabled", wrap="word")
        self.log_textbox.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")

        self.status_label = customtkinter.CTkLabel(self, text="Sẵn sàng", anchor="w")
        self.status_label.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        self.log_queue = queue.Queue()
        self.process_thread = None
        self.stop_event = threading.Event()

        self.process_log_queue()

    def log_message(self, message):
        self.log_queue.put(message)

    def process_log_queue(self):
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.log_textbox.configure(state="normal")
                if message.startswith("STATUS:"):
                    self.status_label.configure(text=message[7:])
                elif message == "PROCESS_FINISHED":
                    self.start_button.configure(state="normal")
                    self.stop_button.configure(state="disabled")
                    self.status_label.configure(text="Hoàn thành!")
                elif message == "PROCESS_STOPPED":
                    self.start_button.configure(state="normal")
                    self.stop_button.configure(state="disabled")
                    self.status_label.configure(text="Đã dừng!")
                else:
                    self.log_textbox.insert("end", message + "\n")
                    self.log_textbox.see("end")
                self.log_textbox.configure(state="disabled")
        except queue.Empty:
            pass
        finally:
            self.after(100, self.process_log_queue)

    def start_processing(self):
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.log_textbox.configure(state="normal")
        self.log_textbox.delete("1.0", "end")
        self.log_textbox.configure(state="disabled")
        self.status_label.configure(text="Bắt đầu...")
        
        self.stop_event.clear()
        self.process_thread = threading.Thread(target=self.run_automation_thread)
        self.process_thread.daemon = True
        self.process_thread.start()

    def stop_processing(self):
        if self.process_thread and self.process_thread.is_alive():
            self.status_label.configure(text="Đang dừng...")
            self.stop_event.set()
            self.stop_button.configure(state="disabled")

    def manual_close_chrome_tabs(self):
        def close_tabs_thread():
            close_all_chrome_tabs(logger=self.log_message)
        threading.Thread(target=close_tabs_thread, daemon=True).start()

    def run_automation_thread(self):
        if not connect_to_device(logger=self.log_message):
            self.log_queue.put("PROCESS_FINISHED")
            return

        if not os.path.exists(ACCOUNTS_FILE):
            self.log_message(f"Lỗi: Không tìm thấy file {ACCOUNTS_FILE}.")
            self.log_queue.put("PROCESS_FINISHED")
            return

        try:
            with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
                lines = [line for line in f.readlines() if line.strip() and "|" in line]
        except Exception as e:
            self.log_message(f"Lỗi khi đọc file {ACCOUNTS_FILE}: {e}")
            self.log_queue.put("PROCESS_FINISHED")
            return

        accounts = [(p[0].strip(), p[1].strip()) for line in lines if len(p := line.split("|")) >= 2 and p[0].strip() and p[1].strip()]
        if not accounts:
            self.log_message("Không có tài khoản hợp lệ nào trong file.")
            self.log_queue.put("PROCESS_FINISHED")
            return

        total_accounts = len(accounts)
        for idx, (username, password) in enumerate(accounts, start=1):
            if self.stop_event.is_set():
                self.log_message("\nQuá trình đã bị dừng bởi người dùng.")
                self.log_queue.put("PROCESS_STOPPED")
                return
            if idx == 1:
                self.log_message(f"\n===== Thiết lập proxy =====")
                proxy = get_new_proxy(API_KEY_KiotProxy)
                apply_proxy_via_adb(proxy['http'], logger=self.log_message)
                self.log_message(f"Proxy đã được thiết lập: {proxy['http']}")
                time.sleep(1)

            self.log_queue.put(f"STATUS:Đang xử lý {idx}/{total_accounts}: {username}")
            self.log_message(f"\n===== XỬ LÝ TÀI KHOẢN {idx}/{total_accounts}: {username} =====")
            
            start_time = time.time()
            new_password = generate_password()
            try:
                change_garena_password(username, password, new_password, self.stop_event, logger=self.log_message)
                
                success_msg = f"{username}|{new_password}|{password}"
                self.log_message(f"✓ THÀNH CÔNG! Đã lưu vào {OUTPUT_FILE}")
                with open(OUTPUT_FILE, "a", encoding="utf-8") as out_f:
                    out_f.write(success_msg + "\n")

            except (RuntimeError, InterruptedError) as e:
                error_msg = f"{username}|{password}|{e}"
                self.log_message(f"✗ LỖI: {username}: {e}")
                with open(ERROR_FILE, "a", encoding="utf-8") as out_f:
                    out_f.write(error_msg + "\n")
            
            end_time = time.time()
            self.log_message(f"Thời gian xử lý: {end_time - start_time:.2f} giây")
            if end_time - start_time < 30:
                delay = 30 - (end_time - start_time)
                time.sleep(delay)
            
            if idx % 4 == 0 and idx < total_accounts:
                if self.stop_event.is_set():
                    break

                self.log_message("\n>>> Đạt mốc 4 tài khoản<<<")
                self.log_message("\n>>> Dọn dẹp Chrome. <<<")
                close_all_chrome_tabs(logger=self.log_message)
                time.sleep(2)

                self.log_message("\n>>> Đổi proxy qua ADB. <<<")
                # change_proxy_via_adb(logger=self.log_message)
                proxy = get_new_proxy(API_KEY_KiotProxy)
                apply_proxy_via_adb(proxy['http'], logger=self.log_message)
                time.sleep(2)

            time.sleep(2)
        
        self.log_message("\n>>> Quá trình hoàn tất, xóa proxy. <<<")
        delete_proxy_via_adb(logger=self.log_message)
        self.log_queue.put("PROCESS_FINISHED" if not self.stop_event.is_set() else "PROCESS_STOPPED")

if __name__ == "__main__":
    if os.name == 'nt':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
        except (AttributeError, ValueError):
            pass
        os.system('chcp 65001 >NUL')

    app = App()
    app.mainloop()

