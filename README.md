# 🛡️ Keyboard Shield

A lightweight, low-level Windows utility designed to rescue laptops suffering from internal hardware keyboard failure (ghost inputs, stuck keys, or liquid damage). 

Instead of paying for expensive physical repairs, **Keyboard Shield** locks onto the specific hardware signature of your broken internal keyboard and silences it, allowing you to use any external USB or wireless keyboard completely uninterrupted.

---

## Features

- **Interactive GUI Calibration (New in v1.1):** Dynamically records the hardware device signature of the broken internal keyboard by displaying a friendly, topmost dark-mode dialog and asking the user to press any key on it.
- **Hardware-Level Discrimination:** Locks block rules strictly to the identified built-in laptop keyboard device ID, leaving any external USB, wireless, or Bluetooth keyboards 100% functional.
- **Fail-Safe Presets (New in v1.1):** Instantly select from predefined block configurations:
  - *Block All Letters & Numbers:* Locks standard keys to stop ghost letters/numbers, leaving modifiers and system shortcuts functional.
  - *Block All Keys (Except Power/Volume/Brightness/PrntScr):* Blocks the entire keyboard layout while safeguarding critical laptop hardware keys (physical Power/Sleep buttons, media volume, display brightness, and Print Screen) to ensure you never get locked out.
- **Safe Driver Shutdown & Hook Release (New in v1.1):** Resolves low-level driver hangs by explicitly clearing device filter hooks (`set_filter` to `0`) and resetting driver context before terminating or on keyboard disconnection, eliminating keyboard freezes.
- **Thread-Safe Queue Architecture (New in v1.1):** Features a robust queue-based messenger system syncing the background interception thread, the detached system tray thread, and the Tkinter UI event loops, avoiding resource deadlocks.
- **Seamless System Tray UI:** Quietly runs in the background. Right-clicking the system tray icon lets users pause/resume blocking, edit custom keys, or recalibrate the target keyboard on the fly.
- **Automated UAC Installer (Updated in v1.1):** Setup launcher auto-requests administrative rights, registers the low-level Interception driver silently (suppressing command window flashing), copies compiled binaries to `%APPDATA%`, and configures autostart in the Windows Startup menu.

---

## How to Use (For Users)

### 1. Installation & Setup
1. Download the project repository folder and extract the contents.
2. Right-click **`Setup_Installer.exe`** and select **Run as Administrator**.
3. A command window will open to register the background device filter. Once finished, **restart your PC** to apply the system changes.

> [!NOTE]
> You only need to run **`Setup_Installer.exe`** **once** to perform the low-level driver registration and startup configuration.
> 
> If you exit Keyboard Shield, you can manually relaunch it at any time by simply opening/double-clicking **`KeyboardShield.exe`** (either from the extracted folder or from the permanent installation folder in `%APPDATA%\KeyboardShield`). You do not need to run the installer again.

### 2. First-Time Calibration
1. When your computer boots back up, a window will appear stating:  
   `ACTION REQUIRED: Press ANY key on the BROKEN keyboard...`
2. Tap any key on your broken built-in keyboard. The app will instantly save its hardware ID and minimize into your taskbar system tray.

### 3. Customizing Your Blocklist
1. Right-click the blue square shield icon in your Windows System Tray (near the clock, you may need to click the carrot `^` arrow to see hidden icons).
2. Click **Choose Keys to Block...**
3. Type out your glitchy keys separated by commas (e.g., `q, w, space`), or choose one of the smart presets:
   - **✨ Block All Letters & Numbers**: Instantly locks standard letters and numbers, leaving modifiers (`Ctrl`, `Alt`, `Shift`), `Delete`, and `Power` working.
   - **🛡️ Block All Keys (Except Power/Volume/Brightness/PrntScr)**: Disables the entire internal keyboard layout while specifically excluding critical laptop system buttons (physical Power/Sleep/Wake keys, volume up/down/mute, screen brightness, and print screen keys).
4. Click **Save Settings**—your laptop keyboard is now shielded!

### 4. Recalibrating the Keyboard
If you need to change the targeted keyboard or perform a re-calibration:
1. Right-click the blue square shield icon in your Windows System Tray.
2. Click **Recalibrate Keyboard...**
3. When the window appears, press any key on the target keyboard you want to disable. The utility will automatically save the updated hardware ID and resume monitoring.

---

## Project Structure

```text
Keyboard-Disabler/
├── install-interception.exe  # Driver registration utility
├── KeyboardShield.exe        # Main background application engine
├── Setup_Installer.exe       # Administrator configuration wizard
├── main.py                   # Python core UI and tray logic source code
├── pynput_interception.py    # Custom Interception driver API wrapper & fallback
└── installer.py              # Python setup wizard source code
```

---

Technical Requirements & Build Stack
OS: Windows 10 / 11

Language: Python 3.12+

Core Libraries: interception-python, pystray, Pillow, pynput

Driver Backend: Interception API Layer

---

Building From Source - 
If you wish to compile the binaries yourself from the Python source scripts, use the following workspace steps:

**1. Install dependencies**  
pip install pystray pillow pyinstaller interception-python pynput

**2. Compile Core background engine**  
pyinstaller --noconsole --onefile --name=KeyboardShield main.py

**3. Compile Installer wizard**  
pyinstaller --onefile --name=Setup_Installer installer.py
