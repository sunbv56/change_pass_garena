import customtkinter
import threading
import queue
import os
import sys
import time

# Import functions from the original scripts
from change_pass_garena import change_garena_password, generate_password, connect_to_device
from close_chrome_tabs import close_all_chrome_tabs

# --- Configuration ---
ACCOUNTS_FILE = "accounts.txt"
OUTPUT_FILE = "output.txt"
ERROR_FILE = "error.txt"
# --- End Configuration ---

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("Garena Password Changer")
        self.geometry("700x500")
        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("blue")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- Controls Frame ---
        self.controls_frame = customtkinter.CTkFrame(self)
        self.controls_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.start_button = customtkinter.CTkButton(self.controls_frame, text="Bắt đầu", command=self.start_processing)
        self.start_button.pack(side="left", padx=5, pady=5)

        self.stop_button = customtkinter.CTkButton(self.controls_frame, text="Dừng", command=self.stop_processing, state="disabled")
        self.stop_button.pack(side="left", padx=5, pady=5)
        
        # Close Chrome Tabs button
        self.close_tabs_button = customtkinter.CTkButton(self.controls_frame, text="🗑️", command=self.close_chrome_tabs, width=40)
        self.close_tabs_button.pack(side="left", padx=5, pady=5)

        # --- Log Textbox ---
        self.log_textbox = customtkinter.CTkTextbox(self, state="disabled", wrap="word")
        self.log_textbox.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")

        # --- Status Bar ---
        self.status_label = customtkinter.CTkLabel(self, text="Sẵn sàng", anchor="w")
        self.status_label.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        # --- Threading and Queue for UI updates ---
        self.log_queue = queue.Queue()
        self.process_thread = None
        self.stop_event = threading.Event()

        self.process_log_queue()

    def log_message(self, message):
        """Safely sends a message to the GUI from any thread."""
        self.log_queue.put(message)

    def process_log_queue(self):
        """Checks the queue for new messages and updates the GUI."""
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
        """Starts the automation process in a new thread."""
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
        """Signals the automation thread to stop."""
        if self.process_thread and self.process_thread.is_alive():
            self.status_label.configure(text="Đang dừng...")
            self.stop_event.set()
            self.stop_button.configure(state="disabled")

    def close_chrome_tabs(self):
        """Manually close all Chrome tabs."""
        def close_tabs_thread():
            try:
                self.log_message("Đang đóng các tab Chrome...")
                close_all_chrome_tabs()
                self.log_message("✅ Đã đóng tất cả tab Chrome.")
            except Exception as e:
                self.log_message(f"❌ Lỗi khi đóng tab Chrome: {e}")
        
        # Run in a separate thread to avoid blocking UI
        threading.Thread(target=close_tabs_thread, daemon=True).start()

    def run_automation_thread(self):
        """The main logic that runs in the background."""
        # Initial checks
        connect_to_device() # Let it print to console

        if not os.path.exists(ACCOUNTS_FILE):
            self.log_message(f"Lỗi: Không tìm thấy file {ACCOUNTS_FILE}.")
            self.log_queue.put("PROCESS_FINISHED")
            return

        try:
            with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
                lines = [line for line in f.readlines() if line.strip() and not line.strip().startswith("#") and "|" in line]
        except Exception as e:
            self.log_message(f"Lỗi khi đọc file {ACCOUNTS_FILE}: {e}")
            self.log_queue.put("PROCESS_FINISHED")
            return

        accounts = []
        for line in lines:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 2 and parts[0] and parts[1]:
                accounts.append((parts[0], parts[1]))
            else:
                self.log_message(f"Bỏ qua dòng không hợp lệ: {line.strip()}")

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
            
            self.log_queue.put(f"STATUS:Đang xử lý tài khoản {idx}/{total_accounts}: {username}")
            self.log_message(f"\n===== XỬ LÝ TÀI KHOẢN {idx}/{total_accounts}: {username} =====")
            
            start_time = time.time()
            new_password = generate_password()
            try:
                # Call the imported function
                # Note: Its detailed output will go to the console, which is fine.
                change_garena_password(username, password, password, new_password)
                
                success_msg = f"{username}|{new_password}|{password}"
                self.log_message(f"✓ THÀNH CÔNG! Thông tin tài khoản đã được lưu vào {OUTPUT_FILE}")
                with open(OUTPUT_FILE, "a", encoding="utf-8") as out_f:
                    out_f.write(success_msg + "\n")

            except Exception as e:
                # The imported function raises RuntimeError on failure, catch it here.
                error_msg = f"{username}|{password}|{e}"
                self.log_message(f"✗ Lỗi khi xử lý tài khoản {username}: {e}")
                with open(ERROR_FILE, "a", encoding="utf-8") as out_f:
                    out_f.write(error_msg + "\n")
            
            end_time = time.time()
            elapsed_time = end_time - start_time
            self.log_message(f"Thời gian chạy: {elapsed_time:.2f} giây")
            
            # Close tabs every 10 accounts
            if idx % 10 == 0 and idx < total_accounts:
                if self.stop_event.is_set():
                    break
                self.log_message("\n>>> Đạt mốc 10 tài khoản, tiến hành đóng các tab Chrome. <<<")
                close_all_chrome_tabs() # This will also print to console
                time.sleep(2)

            time.sleep(2) # Pause between accounts

        self.log_queue.put("PROCESS_FINISHED")

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