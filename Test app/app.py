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
                print("PC shutting down based on GitHub trigger.")
            else:
                print("No shutdown command found in GitHub trigger file.")
        else:
            print(f"Error: Unable to access file, status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    while True:
        check_github_trigger()
        time.sleep(60)  # Check every 60 seconds
