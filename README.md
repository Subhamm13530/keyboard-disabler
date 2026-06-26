# 🛡️ Keyboard Shield

A lightweight, low-level Windows utility designed to rescue laptops suffering from internal hardware keyboard failure (ghost inputs, stuck keys, or liquid damage). 

Instead of paying for expensive physical repairs, **Keyboard Shield** locks onto the specific hardware signature of your broken internal keyboard and silences it, allowing you to use any external USB or wireless keyboard completely uninterrupted.

---

## Features

 **Hardware-Level Discrimination:** Captures the unique device ID of your built-in laptop keyboard. Your external keyboards remain 100% functional and untouched.
 
 **1-Click Total Block Layout:** A built-in smart button instantly blocks all alphanumeric characters (`a-z`, `0-9`) to stop chaotic ghost-typing strings immediately.
 
 **Fail-Safe Operation:** Intentionally keeps critical operating system keys working (like `Ctrl`, `Alt`, `Shift`, `Delete`, and the physical laptop Power button) so you never get locked out (although you can manually lock it if you want).
 
 **Seamless System Tray UI:** Runs silently in the background down by the Windows clock. Easily pause/resume blocking or trigger a hardware recalibration on the fly.
 
 **Automated Installer:** Includes a simple administrative setup wizard to handle low-level driver registration and configure the app to launch safely on Windows startup.

---

## How to Use (For Users)

### 1. Installation
1. Download the project repository folder and extract the contents.
2. Right-click **`Setup_Installer.exe`** and select **Run as Administrator**.
3. A command window will open to register the background device filter. Once finished, **restart your PC** to apply the system changes.

### 2. First-Time Calibration
1. When your computer boots back up, a window will appear stating:  
   `ACTION REQUIRED: Press ANY key on the BROKEN keyboard...`
2. Tap any key on your broken built-in keyboard. The app will instantly save its hardware ID and minimize into your taskbar system tray.

### 3. Customizing Your Blocklist
1. Right-click the blue square shield icon in your Windows System Tray (near the clock).
2. Click **Choose Keys to Block...**
3. Type out your glitchy keys separated by commas (e.g., `q, w, space`), or simply click **✨ Block All Letters & Numbers** for a total automation block.
4. Click **Save Settings**—your laptop keyboard is now shielded!

---

## Project Structure

```text
Keyboard-Disabler/
├── x64/                      # 64-bit low-level driver dependencies
├── x86/                      # 32-bit low-level driver dependencies
├── install-interception.exe  # Driver registration utility
├── KeyboardShield.exe        # Main background application engine
├── Setup_Installer.exe       # Administrator configuration wizard
├── main.py                   # Python core UI and tray logic source code
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
