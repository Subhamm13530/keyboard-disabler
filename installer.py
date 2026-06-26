import os
import sys
import ctypes
import subprocess
import shutil

def is_admin():
    try: return ctypes.windll.shell32.IsUserAnAdmin()
    except: return False

def run_as_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)

def install_app():
    print("=== Keyboard Shield Setup Wizard ===")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    startup_folder = os.path.join(os.getenv('APPDATA'), r'Microsoft\Windows\Start Menu\Programs\Startup')
    
    app_source = os.path.join(current_dir, "KeyboardShield.exe")
    driver_installer = os.path.join(current_dir, "install-interception.exe")

    print("\n[1/3] Copying application package to startup tracking...")
    if os.path.exists(app_source):
        shutil.copy(app_source, startup_folder)
        print("Success: Registered.")
    else:
        print("Error: KeyboardShield.exe compiled build is missing!")
        input("\nPress Enter to exit...")
        return

    print("\n[2/3] Registering hardware layer filter system...")
    if os.path.exists(driver_installer):
        try:
            result = subprocess.run([driver_installer, "/install"], capture_output=True, text=True)
            print(result.stdout)
        except Exception as e:
            print(f"Driver integration failure: {e}")
    else:
        print("Error: driver installer executable missing!")
        input("\nPress Enter to exit...")
        return

    print("\n[3/3] System Modification Complete!")
    print("------------------------------------------------------------------")
    print("MANDATORY: You must restart your PC right now to activate.")
    print("------------------------------------------------------------------")
    input("\nPress Enter to close setup...")

if __name__ == "__main__":
    if is_admin(): install_app()
    else: run_as_admin()