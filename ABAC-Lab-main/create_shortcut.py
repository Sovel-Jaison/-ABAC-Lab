import os
import sys
import platform
import subprocess

APP_NAME = "ABAC Lab" 
ICON_PATH = os.path.abspath("res/desktop_logo.ico") # Windows uses .ico format

def create_windows_shortcut():
    """Create a desktop shortcut on Windows."""
    SCRIPT_NAME = "gui.py"  # Windows runs
    try:
        import winshell
        from win32com.client import Dispatch

        desktop = winshell.desktop()
        shortcut_path = os.path.join(desktop, f"{APP_NAME}.lnk")

        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortcut(shortcut_path)
        shortcut.TargetPath = sys.executable  # Use Python executable
        shortcut.Arguments = os.path.abspath(SCRIPT_NAME)
        shortcut.WorkingDirectory = os.path.dirname(os.path.abspath(SCRIPT_NAME))
        shortcut.IconLocation = ICON_PATH
        shortcut.Save()

        print(f"Windows shortcut created: {shortcut_path}")
    except ImportError:
        print("Error: `winshell` module is required for Windows shortcuts. Run `pip install pywin32 winshell`.")
    
def create_linux_shortcut():
    """Create a .desktop shortcut for Linux users."""
    home_dir = os.path.expanduser("~")
    desktop_dir = os.path.join(home_dir, "Desktop")
    applications_dir = os.path.join(home_dir, ".local/share/applications")
    
    # Ensure directories exist
    os.makedirs(applications_dir, exist_ok=True)
    os.makedirs(desktop_dir, exist_ok=True)

    desktop_file_path = os.path.join(desktop_dir, "ABAC_Lab.desktop")

    desktop_content = f"""[Desktop Entry]
Name=ABAC Lab
Exec={os.path.abspath("linux_run_app.sh")}
Icon={os.path.abspath("res/desktop.png")}
Terminal=false
Type=Application
Categories=Utility;
"""

    # Write the desktop file
    with open(desktop_file_path, "w") as f:
        f.write(desktop_content)
    
    os.chmod(desktop_file_path, 0o755)

    # Copy to applications directory for better integration
    applications_shortcut = os.path.join(applications_dir, "ABAC_Lab.desktop")
    os.system(f"cp {desktop_file_path} {applications_shortcut}")

    print(f"Shortcut created successfully: {desktop_file_path}")

def create_shortcut():
    """Determine the OS and create the appropriate shortcut."""
    system = platform.system()

    if system == "Windows":
        create_windows_shortcut()
    elif system == "Linux":
        create_linux_shortcut()
    else:
        print("Unsupported OS")

if __name__ == "__main__":
    print(f"Installing {APP_NAME}...")
    create_shortcut()
