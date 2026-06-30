import os
import sys
import threading
import queue
import ctypes
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item
from pynput_interception import KeyboardFilter, KeyboardListener

CONFIG_DIR = os.path.join(os.getenv('APPDATA'), 'KeyboardShield')
ID_FILE = os.path.join(CONFIG_DIR, 'keyboard_id.txt')
KEYS_FILE = os.path.join(CONFIG_DIR, 'blocked_keys.txt')

DEFAULT_KEYS = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

is_blocking_active = True
internal_keyboard_id = None
blocked_keys = set()
icon = None
filter_stream = None
_stop_event = threading.Event()
_gui_queue = queue.Queue()

class CalibrationDialog(tk.Toplevel):
    def __init__(self, parent, on_success, on_cancel=None):
        super().__init__(parent)
        self.on_success = on_success
        self.on_cancel = on_cancel
        self.device_id = None
        self.listener = None
        self.listener_thread = None
        
        self.title("Keyboard Calibration")
        self.geometry("420x240")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.grab_set()
        
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
        self.configure(bg="#1E1E1E")
        
        self.label_title = tk.Label(
            self, 
            text="Calibrating Keyboard", 
            font=("Segoe UI", 15, "bold"), 
            bg="#1E1E1E", 
            fg="#0078D7"
        )
        self.label_title.pack(pady=15)
        
        self.label_instructions = tk.Label(
            self, 
            text="ACTION REQUIRED:\nPress ANY key on the BROKEN keyboard\n(the one you wish to disable).", 
            font=("Segoe UI", 11), 
            bg="#1E1E1E", 
            fg="#FFFFFF",
            justify="center"
        )
        self.label_instructions.pack(pady=10)
        
        self.cancel_btn = tk.Button(
            self, 
            text="Cancel", 
            command=self.on_close,
            bg="#3E3E42", 
            fg="#FFFFFF", 
            activebackground="#505050", 
            activeforeground="#FFFFFF",
            bd=0, 
            padx=20, 
            pady=6, 
            font=("Segoe UI", 10, "bold"),
            cursor="hand2"
        )
        self.cancel_btn.pack(pady=15)
        
        self.start_listener()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
    def start_listener(self):
        def run_listener():
            try:
                def on_press(key, device):
                    self.device_id = str(device)
                    self.after(0, self.calibration_completed)
                    return False
                
                with KeyboardListener(on_press=on_press) as listener:
                    self.listener = listener
                    listener.join()
            except Exception as e:
                self.after(0, lambda: self.on_error(e))
                
        self.listener_thread = threading.Thread(target=run_listener, daemon=True)
        self.listener_thread.start()
        
    def calibration_completed(self):
        if self.device_id:
            self.on_success(self.device_id)
        self.cleanup_and_destroy()
        
    def on_error(self, err):
        messagebox.showerror("Driver Error", f"Failed to start calibration listener:\n{err}", parent=self)
        if self.on_cancel:
            self.on_cancel()
        self.cleanup_and_destroy()
        
    def on_close(self):
        if self.on_cancel:
            self.on_cancel()
        self.cleanup_and_destroy()
        
    def cleanup_and_destroy(self):
        if self.listener:
            self.listener.running = False
        try:
            self.grab_release()
        except Exception:
            pass
        self.destroy()

def load_config():
    global blocked_keys
    os.makedirs(CONFIG_DIR, exist_ok=True)

    if os.path.exists(KEYS_FILE):
        with open(KEYS_FILE, 'r') as f:
            blocked_keys = {line.strip().lower() for line in f.readlines() if line.strip()}
    else:
        blocked_keys = set(DEFAULT_KEYS)
        save_blocked_keys()

def save_blocked_keys():
    with open(KEYS_FILE, 'w') as f:
        for key in blocked_keys:
            f.write(f"{key}\n")

def keyboard_worker():
    global filter_stream
    def filter_callback(event):
        global is_blocking_active, internal_keyboard_id, blocked_keys
        if not is_blocking_active or not internal_keyboard_id:
            return event

        if str(event.device) == internal_keyboard_id:
            if str(event.key).lower() in blocked_keys:
                return None
        return event

    with KeyboardFilter(callback=filter_callback) as filter_stream:
        _stop_event.wait()
        filter_stream.running = False

def _show_custom_keys_window():
    global blocked_keys

    win = tk.Toplevel()
    win.title("Configure Blocked Keys")
    win.geometry("450x400")
    win.resizable(False, False)
    win.attributes("-topmost", True)
    win.grab_set()

    win.focus_force()

    tk.Label(win, text="Enter keys to block (separated by commas):", font=("Arial", 11, "bold")).pack(pady=10)

    entry = tk.Entry(win, width=45, font=("Arial", 12))
    entry.insert(0, ", ".join(sorted(list(blocked_keys))))
    entry.pack(pady=10)
    entry.focus_set()

    def load_preset_alphanumeric():
        letters = [chr(i) for i in range(ord('a'), ord('z') + 1)]
        numbers = [str(i) for i in range(10)]
        full_preset = letters + numbers
        entry.delete(0, tk.END)
        entry.insert(0, ", ".join(full_preset))

    def load_preset_all_except_system():
        all_keys = [
            'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
            '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
            'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12',
            'shift', 'left shift', 'right shift', 'ctrl', 'left ctrl', 'right ctrl', 'alt', 'left alt', 'right alt', 'windows', 'left windows', 'right windows', 'apps', 'menu', 'alt gr',
            'insert', 'delete', 'home', 'end', 'page up', 'page down', 'up', 'down', 'left', 'right',
            '`', '~', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '_', '+', '-', '=', '[', ']', '{', '}', '\\', '|', ';', ':', '\'', '"', ',', '<', '.', '>', '/', '?',
            'numpad 0', 'numpad 1', 'numpad 2', 'numpad 3', 'numpad 4', 'numpad 5', 'numpad 6', 'numpad 7', 'numpad 8', 'numpad 9',
            'numpad /', 'numpad *', 'numpad -', 'numpad +', 'numpad enter', 'numpad .', 'num lock',
            'space', 'backspace', 'tab', 'enter', 'caps lock', 'escape', 'esc', 'scroll lock'
        ]
        entry.delete(0, tk.END)
        entry.insert(0, ", ".join(all_keys))

    def save_changes():
        global blocked_keys
        raw_input = entry.get()
        blocked_keys = {k.strip().lower() for k in raw_input.split(",") if k.strip()}
        save_blocked_keys()
        messagebox.showinfo("Success", "Blocked keys updated successfully!", parent=win)
        win.destroy()

    preset_btn = tk.Button(win, text="✨ Block All Letters & Numbers", command=load_preset_alphanumeric,
                           bg="#E1DFDD", fg="black", font=("Arial", 9, "bold"))
    preset_btn.pack(pady=4)

    preset_all_btn = tk.Button(win, text="🛡️ Block All Keys (Except Power/Volume/Brightness/PrntScr)", 
                               command=load_preset_all_except_system,
                               bg="#E1DFDD", fg="black", font=("Arial", 9, "bold"))
    preset_all_btn.pack(pady=4)

    tk.Label(win, text="The alphanumeric preset leaves modifiers/system keys working.\nThe Block All preset keeps power, sleep, wake, print screen, and media/volume keys working.",
             font=("Arial", 8, "italic"), fg="gray", wraplength=410).pack(pady=10)

    save_btn = tk.Button(win, text="Save Settings", command=save_changes,
                         bg="#0078D7", fg="white", width=18, font=("Arial", 10, "bold"))
    save_btn.pack(pady=10)

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
    _gui_queue.put("recalibrate")

def on_quit(icon, item):
    _stop_event.set()
    icon.stop()
    _gui_queue.put(None)

def open_custom_keys_window(icon, item):
    _gui_queue.put("open_keys_window")

def setup_system_tray():
    global icon
    menu = (
        item('Blocker Active', toggle_action, checked=lambda item: is_blocking_active),
        item('Choose Keys to Block...', open_custom_keys_window),
        item('Recalibrate Keyboard...', reset_calibration),
        item('Exit App', on_quit)
    )
    icon = pystray.Icon("KeyboardShield", create_icon_image(), "Keyboard Shield: ACTIVE", menu)
    icon.run_detached()

def run_main_loop(root: tk.Tk):
    try:
        msg = _gui_queue.get_nowait()
        if msg is None:
            root.quit()
            return
        elif msg == "open_keys_window":
            _show_custom_keys_window()
        elif msg == "recalibrate":
            _show_calibration_window(is_startup=False)
    except queue.Empty:
        pass
    root.after(100, run_main_loop, root)

_kb_thread = None

def start_application_services():
    global _kb_thread
    _kb_thread = threading.Thread(target=keyboard_worker, daemon=False)
    _kb_thread.start()
    setup_system_tray()

def _show_calibration_window(is_startup=False):
    def on_success(device_id):
        global internal_keyboard_id
        internal_keyboard_id = device_id
        with open(ID_FILE, 'w') as f:
            f.write(internal_keyboard_id)
        
        if is_startup:
            start_application_services()
            
    def on_cancel():
        if is_startup:
            root.quit()

    CalibrationDialog(root, on_success, on_cancel)

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    try:
        load_config()
    except RuntimeError as e:
        messagebox.showerror("Interception Driver Missing", str(e))
        sys.exit(1)

    _show_calibration_window(is_startup=True)
    root.after(100, run_main_loop, root)
    root.mainloop()

    if _kb_thread and _kb_thread.is_alive():
        _kb_thread.join(timeout=3)
    if icon:
        try:
            icon.stop()
        except Exception:
            pass
    sys.exit(0)