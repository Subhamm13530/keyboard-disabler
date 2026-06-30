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
    # Dynamic path mapping to ensure we track the extracted source files folder
    BASE_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))
    keyboard_shield_path = os.path.join(BASE_DIR, "KeyboardShield.exe")
    driver_installer_path = os.path.join(BASE_DIR, "install-interception.exe")
    
    print("=== Keyboard Shield Setup Wizard ===")
    
    # 1. Verification checks before modifying system files
    if not os.path.exists(keyboard_shield_path):
        print("Error: KeyboardShield.exe compiled build is missing from source folder!")
        input("\nPress Enter to exit...")
        return

    if not os.path.exists(driver_installer_path):
        print("Error: Required framework driver 'install-interception.exe' is missing!")
        input("\nPress Enter to exit...")
        return

    try:
        print("\n[1/3] Deploying application binary assets...")
        # Define permanent application home directory paths
        target_dir = os.path.join(os.getenv('APPDATA'), 'KeyboardShield')
        os.makedirs(target_dir, exist_ok=True)
        
        # Copy the core utility engine into the application data path
        deployed_app_path = os.path.join(target_dir, "KeyboardShield.exe")
        shutil.copy2(keyboard_shield_path, deployed_app_path)
        
        # Create a persistent link inside the Windows Startup folder so it boots automatically
        startup_dir = os.path.join(os.environ["APPDATA"], "Microsoft\\Windows\\Start Menu\\Programs\\Startup")
        startup_shortcut_path = os.path.join(startup_dir, "KeyboardShield.exe")
        
        # Copying the binary directly to Startup ensures Windows loads it seamlessly on user sign-in
        shutil.copy2(deployed_app_path, startup_shortcut_path)
        print(" -> Application successfully configured to run on Windows startup.")
        
        print("\n[2/3] Registering driver execution dependencies...")
        # Execute the interception installer component using a silent background subprocess
        # /install tells the driver tool to write the filtering hooks into the system registry
        process = subprocess.run(
            [driver_installer_path, "/install"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        if process.returncode == 0:
            print(" -> Low-level system driver registration completed successfully.")
        else:
            print(f" -> Driver Warning: System reported status context: {process.stdout.strip()}")
        
        print("\n[3/3] Finalizing installation environment configurations...")
        print("\n==========================================================")
        print("SUCCESS: Keyboard Shield has been installed successfully!")
        print("CRITICAL: You MUST restart your computer to apply the updates.")
        print("==========================================================")
        
    except Exception as e:
        print(f"\nCRITICAL ERROR occurred during installation: {e}")
        
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    if is_admin():
        install_app()
    else:
        print("Requesting administrator privileges...")
        run_as_admin()