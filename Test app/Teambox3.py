import os
import requests
import time

# Use the raw GitHub file URL
GITHUB_REPO_URL = "https://raw.githubusercontent.com/rikeshkumarrk/shutdown-trigger/main/trigger.txt"

def shutdown_pc():
    os.system("shutdown /s /t 1")

def check_github_trigger():
    try:
        response = requests.get(GITHUB_REPO_URL)
        if response.status_code == 200:
            content = response.text.strip()
            if content.upper() == "SHUTDOWN":
                shutdown_pc()
        # No else condition to avoid print statements
    except Exception as e:
        pass  # Ignore exceptions silently

if __name__ == "__main__":
    while True:
        check_github_trigger()
        time.sleep(180)  # Check every 180 seconds (3 minutes)
