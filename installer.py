import os
import sys
import ctypes
import subprocess
import shutil

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    # Relaunches the current script with full administrative tokens
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)

def install_app():
    # Fixes the System32 path redirection bug by grabbing the REAL directory right here
    BASE_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))
    keyboard_shield_path = os.path.join(BASE_DIR, "KeyboardShield.exe")
    
    print("=== Keyboard Shield Setup Wizard ===")
    print("[1/3] Copying application package to startup tracking...")
    
    # Verify the target build sits in the same directory as this setup script
    if not os.path.exists(keyboard_shield_path):
        print("Error: KeyboardShield.exe compiled build is missing!")
        print(f"Looked inside: {BASE_DIR}")
        input("\nPress Enter to exit...")
        return

    try:
        # --- [YOUR INSTALLATION LOGIC HERE] ---
        # Example: Copying files to an installation or startup directory
        # destination = os.path.join(os.environ["APPDATA"], "Microsoft\\Windows\\Start Menu\\Programs\\Startup")
        # shutil.copy(keyboard_shield_path, destination)
        
        print("[2/3] Registering driver execution dependencies...")
        # Your sub-process driver implementation details go here
        
        print("[3/3] Installation completed successfully!")
        print("\nSUCCESS: Please RESTART your computer to apply the system filter updates.")
        
    except Exception as e:
        print(f"\nAn error occurred during installation: {e}")
        
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    if is_admin():
        install_app()
    else:
        print("Requesting administrator privileges...")
        run_as_admin()