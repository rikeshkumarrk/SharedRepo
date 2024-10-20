import os
import requests
import time
import ctypes
import keyboard
import threading
import pyautogui

GITHUB_REPO_URL = "https://raw.githubusercontent.com/rikeshkumarrk/shutdown-trigger/main/trigger.txt"
mouse_restriction_event = threading.Event()  # Event to control mouse restriction

def show_access_denied_popup():
    ctypes.windll.user32.MessageBoxW(0, "Access Denied", "Security Alert", 0x10 | 0x0)

def restrict_keyboard():
    keyboard.block_key("all")

def restrict_mouse():
    # Continuously lock the mouse to the center of the screen and block all mouse actions
    screen_width, screen_height = pyautogui.size()
    center_x, center_y = screen_width // 2, screen_height // 2
    while mouse_restriction_event.is_set():  # Run while the event is set
        # Move the mouse to the center
        pyautogui.moveTo(center_x, center_y)
        # Hold down all mouse buttons to disable them
        pyautogui.mouseDown(button='left')
        pyautogui.mouseDown(button='right')
        pyautogui.mouseDown(button='middle')  # Middle button (scroll wheel) click

# Flag to track if restrictions are active
restrictions_active = False

def check_github_trigger():
    global restrictions_active
    try:
        response = requests.get(GITHUB_REPO_URL)
        if response.status_code == 200:
            content = response.text.strip()
            if content.upper() == "DENY":
                if not restrictions_active:  # Only activate restrictions if not already active
                    show_access_denied_popup()
                    restrict_keyboard()  # Block keyboard
                    restrictions_active = True
                    mouse_restriction_event.set()  # Set the event to start mouse restriction
                    threading.Thread(target=restrict_mouse, daemon=True).start()
                    print("Access denied popup displayed and activity restricted.")
            else:
                if restrictions_active:  # Only unrestrict if restrictions are active
                    restrictions_active = False
                    mouse_restriction_event.clear()  # Clear the event to stop mouse restriction
                    print("Access is now granted. Restrictions lifted.")
        else:
            print(f"Error: Unable to access file, status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    while True:
        check_github_trigger()
        time.sleep(60)  # Check every 60 seconds
