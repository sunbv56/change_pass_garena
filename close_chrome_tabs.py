import subprocess
import time
import sys
import os

# --- Configuration ---
LDPLAYER_ADB_ADDRESS = "localhost:5555"
CHROME_PACKAGE_NAME = "com.android.chrome"
CHROME_MAIN_ACTIVITY = "com.google.android.apps.chrome.Main"
# --- End Configuration ---

# Ensure UTF-8 output on Windows consoles
if os.name == 'nt':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except (AttributeError, ValueError):
        pass
    os.system('chcp 65001 >NUL')

def run_adb_command(command, timeout=15):
    """Runs a complete ADB command and returns its output."""
    full_command = f"adb -s {LDPLAYER_ADB_ADDRESS} {command}"
    try:
        print(f"Executing: {full_command}")
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
        print("\nError: 'adb' command not found.")
        print("Please ensure the Android SDK Platform-Tools are installed and 'adb' is in your system's PATH.")
        return None, "ADB not found"
    except subprocess.CalledProcessError as e:
        print(f"\nCommand failed: {full_command}")
        return e.stdout.strip(), e.stderr.strip()
    except subprocess.TimeoutExpired:
        print(f"\nADB command timed out: {full_command}")
        return None, "Command timed out"

def connect_to_device():
    """Tries to connect to the specified ADB address."""
    print(f"Attempting to connect to LDPlayer at {LDPLAYER_ADB_ADDRESS}...")
    connect_command = f"adb connect {LDPLAYER_ADB_ADDRESS}"
    subprocess.run(connect_command, shell=True, capture_output=True)
    time.sleep(1) # Give it a moment to connect

    # Verify connection
    result = subprocess.run("adb devices", shell=True, capture_output=True, text=True)
    if LDPLAYER_ADB_ADDRESS in result.stdout:
        print(f"Successfully connected to {LDPLAYER_ADB_ADDRESS}.")
        return True
    else:
        print(f"\nFailed to connect to LDPlayer at {LDPLAYER_ADB_ADDRESS}.")
        print("Please ensure LDPlayer is running and ADB/USB Debugging is enabled.")
        return False

def close_all_chrome_tabs():
    """
    Closes all Chrome tabs by performing 5 clicks to close tabs.
    This method uses ADB input tap commands to simulate user clicks.
    """
    if not connect_to_device():
        return

    print("\nStarting Chrome and performing 5 clicks to close tabs...")
    
    # First, start Chrome
    start_command = f"shell am start -n {CHROME_PACKAGE_NAME}/{CHROME_MAIN_ACTIVITY}"
    stdout, stderr = run_adb_command(start_command)
    
    if stderr and "Error" in stderr:
        print(f"\nError starting Chrome: {stderr}")
        return
    
    print("Chrome started successfully. Performing 5 clicks to close tabs...")
    
    # Wait a moment for Chrome to fully load
    time.sleep(2)
    
    # Define click coordinates (you may need to adjust these based on your screen resolution)
    # These are approximate coordinates for the tab close button area
    click_coordinates = [
        (431, 77),  # Click 1 - top right area where close button usually is
        (503, 79),   # Click 2 - slightly left of first click
        (185, 225),   # Click 3 - further left
        (334, 592),   # Click 4 - even further left
        (43, 80)    # Click 5 - final click
    ]
    
    for i, (x, y) in enumerate(click_coordinates, 1):
        print(f"Performing click {i}/5 at coordinates ({x}, {y})...")
        
        # Perform the click
        click_command = f"shell input tap {x} {y}"
        stdout, stderr = run_adb_command(click_command)
        
        if stderr and "Error" in stderr:
            print(f"Error with click {i}: {stderr}")
        else:
            print(f"✅ Click {i} completed successfully.")
        
        # Small delay between clicks
        time.sleep(0.5)
    
    print("\n✅ All 5 clicks completed successfully.")
    print("Chrome tabs should now be closed.")

if __name__ == "__main__":
    close_all_chrome_tabs()
    time.sleep(3)
