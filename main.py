import os
import sys
import threading
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item
from pynput_interception import KeyboardFilter, KeyboardListener

# CONFIGURATION PATHS
CONFIG_DIR = os.path.join(os.getenv('APPDATA'), 'KeyboardShield')
ID_FILE = os.path.join(CONFIG_DIR, 'keyboard_id.txt')
KEYS_FILE = os.path.join(CONFIG_DIR, 'blocked_keys.txt')

# Default keys to block if they haven't chosen any yet
DEFAULT_KEYS = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

is_blocking_active = True
internal_keyboard_id = None
blocked_keys = []
icon = None

# --- FILE MANAGEMENT ---
def load_config():
    global internal_keyboard_id, blocked_keys
    os.makedirs(CONFIG_DIR, exist_ok=True)
    
    if os.path.exists(ID_FILE):
        with open(ID_FILE, 'r') as f:
            internal_keyboard_id = f.read().strip()
    else:
        calibrate_hardware()

    if os.path.exists(KEYS_FILE):
        with open(KEYS_FILE, 'r') as f:
            blocked_keys = [line.strip().lower() for line in f.readlines() if line.strip()]
    else:
        blocked_keys = DEFAULT_KEYS
        save_blocked_keys()

def save_blocked_keys():
    with open(KEYS_FILE, 'w') as f:
        for key in blocked_keys:
            f.write(f"{key}\n")

def calibrate_hardware():
    global internal_keyboard_id
    print("\n==========================================================")
    print("ACTION REQUIRED: Press ANY key on the BROKEN keyboard...")
    print("==========================================================")
    
    def on_press(key, device):
        global internal_keyboard_id
        internal_keyboard_id = str(device)
        with open(ID_FILE, 'w') as f:
            f.write(internal_keyboard_id)
        return False 

    with KeyboardListener(on_press=on_press) as listener:
        listener.join()

# --- THE LOGIC ENGINE ---
def keyboard_worker():
    def filter_callback(event):
        global is_blocking_active, internal_keyboard_id, blocked_keys
        if not is_blocking_active or not internal_keyboard_id:
            return event 

        if str(event.device) == internal_keyboard_id:
            if str(event.key).lower() in blocked_keys:
                return None # Suppress the key
        return event

    with KeyboardFilter(callback=filter_callback) as filter_stream:
        filter_stream.join()

# --- CONFIGURATION WINDOW (GUI) ---
def open_custom_keys_window():
    global blocked_keys
    
    root = tk.Tk()
    root.title("Configure Blocked Keys")
    root.geometry("400x320")
    root.attributes("-topmost", True)

    tk.Label(root, text="Enter keys to block (separated by commas):", font=("Arial", 11, "bold")).pack(pady=10)

    entry = tk.Entry(root, width=38, font=("Arial", 12))
    entry.insert(0, ", ".join(blocked_keys))
    entry.pack(pady=10)

    # --- NEW SHORTCUT FUNCTIONS ---
    def load_preset_alphanumeric():
        """Automatically generates all lower/upper letters and 0-9 numbers."""
        letters = [chr(i) for i in range(ord('a'), ord('z')+1)]
        numbers = [str(i) for i in range(10)]
        full_preset = letters + numbers
        
        entry.delete(0, tk.END)
        entry.insert(0, ", ".join(full_preset))

    def save_changes():
        global blocked_keys
        raw_input = entry.get()
        blocked_keys = [k.strip().lower() for k in raw_input.split(",") if k.strip()]
        save_blocked_keys()
        messagebox.showinfo("Success", "Blocked keys updated successfully!")
        root.destroy()

    # Quick Action Preset Button
    preset_btn = tk.Button(root, text="✨ Block All Letters & Numbers", command=load_preset_alphanumeric, bg="#E1DFDD", fg="black", font=("Arial", 9, "bold"))
    preset_btn.pack(pady=5)

    tk.Label(root, text="This safely leaves Ctrl, Alt, Shift, Delete, and Power completely working.", font=("Arial", 8, "italic"), fg="gray", wraplength=350).pack(pady=10)

    # Save button
    save_btn = tk.Button(root, text="Save Settings", command=save_changes, bg="#0078D7", fg="white", width=18, font=("Arial", 10, "bold"))
    save_btn.pack(pady=15)
    
    root.mainloop()

# --- SYSTEM TRAY INTERFACE ---
def create_icon_image():
    image = Image.new('RGB', (64, 64), color='black')
    dc = ImageDraw.Draw(image)
    dc.rectangle([16, 16, 48, 48], fill='#0078D7') 
    return image

def toggle_action(icon, item):
    global is_blocking_active
    is_blocking_active = not is_blocking_active
    icon.title = "Keyboard Shield: ACTIVE" if is_blocking_active else "Keyboard Shield: PAUSED"

def reset_calibration(icon, item):
    global internal_keyboard_id
    if os.path.exists(ID_FILE): os.remove(ID_FILE)
    icon.stop() 
    load_config()
    setup_system_tray()

def on_quit(icon, item):
    icon.stop()
    sys.exit(0)

def setup_system_tray():
    global icon
    menu = (
        item('Blocker Active', toggle_action, checked=lambda item: is_blocking_active),
        item('Choose Keys to Block...', lambda: threading.Thread(target=open_custom_keys_window).start()),
        item('Recalibrate Keyboard...', reset_calibration),
        item('Exit App', on_quit)
    )
    icon = pystray.Icon("KeyboardShield", create_icon_image(), "Keyboard Shield: ACTIVE", menu)
    icon.run()

if __name__ == "__main__":
    load_config()
    threading.Thread(target=keyboard_worker, daemon=True).start()
    setup_system_tray()