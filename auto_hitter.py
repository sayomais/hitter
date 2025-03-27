import pyautogui
import keyboard
import time
import sys

# Safety feature to prevent the program from running indefinitely
pyautogui.FAILSAFE = True

def auto_hit():
    print("Auto Hitter Started!")
    print("Press 'F6' to start/stop clicking")
    print("Press 'F7' to exit the program")
    
    clicking = False
    
    while True:
        if keyboard.is_pressed('f6'):
            clicking = not clicking
            print(f"Clicking {'Started' if clicking else 'Stopped'}")
            time.sleep(0.5)  # Prevent multiple toggles
            
        if keyboard.is_pressed('f7'):
            print("Exiting program...")
            sys.exit()
            
        if clicking:
            pyautogui.click()
            time.sleep(1)  # Wait 1 second between clicks

if __name__ == "__main__":
    print("Auto Hitter Program")
    print("------------------")
    print("Instructions:")
    print("1. Run this program")
    print("2. Press F6 to start/stop clicking")
    print("3. Press F7 to exit")
    print("4. Move your mouse to the desired position")
    print("5. The program will click every second when active")
    print("\nStarting in 3 seconds...")
    time.sleep(3)
    auto_hit() 