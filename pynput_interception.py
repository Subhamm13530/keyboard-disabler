import ctypes
import threading
from typing import Callable, Optional
from interception import Interception

def get_key_name(scan_code: int, is_extended: bool = False) -> str:
    # Form the parameter for GetKeyNameTextW
    # lParam layout:
    # 0-15: Repeat count (not used)
    # 16-23: Scan code
    # 24: Extended-key flag
    # 25: Do not care (1 to distinguish left/right, 0 otherwise)
    lParam = (scan_code & 0xFF) << 16
    if is_extended:
        lParam |= (1 << 24)
    
    buf = ctypes.create_unicode_buffer(128)
    ctypes.windll.user32.GetKeyNameTextW(lParam, buf, 128)
    return buf.value.lower()

class Event:
    def __init__(self, device: int, code: int, flags: int):
        self.device = device
        self.code = code
        self.flags = flags
        self.key = get_key_name(code, bool(flags & 2))

class KeyboardListener:
    def __init__(self, on_press: Callable[[str, int], Optional[bool]]):
        self.on_press = on_press
        self.running = False
        self._thread = None
        self.context = None

    def __enter__(self):
        self.context = Interception()
        if not self.context.valid:
            raise RuntimeError(
                "Interception driver is not installed or not running.\n"
                "Please run 'install-interception.exe' as Administrator and reboot, "
                "then try again."
            )
        self.context.set_filter(self.context.is_keyboard, 0xFFFF)
        self.running = True
        self._thread = threading.Thread(target=self._run)
        self._thread.daemon = True
        self._thread.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.running = False
        if self.context:
            # CRITICAL: Clear the filter FIRST so the driver stops intercepting.
            # If we destroy() without clearing, the driver keeps holding key events
            # in its buffer with no one to forward them -> keyboard freeze until reboot.
            try:
                self.context.set_filter(self.context.is_keyboard, 0)
            except Exception:
                pass
            try:
                self.context.destroy()
            except Exception:
                pass
            self.context = None

    def join(self):
        if self._thread:
            self._thread.join()

    def _run(self):
        while self.running:
            try:
                device_id = self.context.await_input(100)
            except Exception:
                break
            if device_id is None:
                continue
            
            try:
                stroke = self.context.devices[device_id].receive()
            except Exception:
                # Device disappeared (e.g. keyboard disconnected) – skip
                continue

            if stroke is None:
                # No stroke data: device likely disconnected mid-intercept.
                # Do NOT leave the stroke hanging in the driver buffer.
                continue

            # Always forward first so a disconnect can never leave keys stuck.
            try:
                self.context.send(device_id, stroke)
            except Exception:
                continue

            # Check for key down event (flags & 1 == 0)
            if (stroke.flags & 1) == 0:
                key_name = get_key_name(stroke.code, bool(stroke.flags & 2))
                try:
                    res = self.on_press(key_name, device_id)
                    if res is False:
                        self.running = False
                        break
                except Exception:
                    pass

class KeyboardFilter:
    def __init__(self, callback: Callable[[Event], Optional[Event]]):
        self.callback = callback
        self.running = False
        self._thread = None
        self.context = None

    def __enter__(self):
        self.context = Interception()
        if not self.context.valid:
            raise RuntimeError(
                "Interception driver is not installed or not running.\n"
                "Please run 'install-interception.exe' as Administrator and reboot, "
                "then try again."
            )
        self.context.set_filter(self.context.is_keyboard, 0xFFFF)
        self.running = True
        self._thread = threading.Thread(target=self._run)
        self._thread.daemon = True
        self._thread.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.running = False
        if self.context:
            # CRITICAL: Clear the filter FIRST so the driver stops intercepting.
            # If we destroy() without clearing, the driver keeps holding key events
            # in its buffer with no one to forward them -> keyboard freeze until reboot.
            try:
                self.context.set_filter(self.context.is_keyboard, 0)
            except Exception:
                pass
            try:
                self.context.destroy()
            except Exception:
                pass
            self.context = None

    def join(self):
        if self._thread:
            self._thread.join()

    def _run(self):
        while self.running:
            try:
                device_id = self.context.await_input(100)
            except Exception:
                break
            if device_id is None:
                continue

            try:
                stroke = self.context.devices[device_id].receive()
            except Exception:
                # Device disappeared (e.g. keyboard disconnected) – skip
                continue

            if stroke is None:
                # No stroke data: device likely disconnected mid-intercept.
                # Do NOT leave the stroke hanging in the driver buffer.
                continue

            event = Event(device_id, stroke.code, stroke.flags)
            try:
                res_event = self.callback(event)
            except Exception:
                res_event = event  # default to forward on callback error

            if res_event is not None:
                try:
                    self.context.send(device_id, stroke)
                except Exception:
                    pass
