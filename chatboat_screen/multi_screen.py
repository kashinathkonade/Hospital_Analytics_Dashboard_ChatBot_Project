import time
import pyautogui
from pynput import keyboard

# Define a flag to control the loop
stop_flag = False

# Function to detect key press
def on_press(key):
    global stop_flag
    try:
        # Stop when 'Esc' key is pressed
        if key == keyboard.Key.esc:
            stop_flag = True
            print("Esc key pressed. Stopping...")
            return False  # Stop listening for keypresses
    except Exception as e:
        print(f"Error: {e}")

# Start listening for the 'Esc' key in a separate thread
listener = keyboard.Listener(on_press=on_press)
listener.start()

# Main loop
while not stop_flag:  # Run until the 'Esc' key is pressed
    for i in range(50):
        if stop_flag:  # Check flag frequently
            break
        pyautogui.moveTo(i * 10, 5)

    for i in range(50):
        if stop_flag:  # Check flag frequently
            break
        pyautogui.moveTo(5, (50 - i) * 10)

    if stop_flag:  # Check flag before each action
        break

    pyautogui.hotkey('alt', 'tab')

    for i in range(2):
        if stop_flag:  # Check flag frequently
            break
        time.sleep(0.1)  # Use shorter sleep intervals for quicker response
        pyautogui.hotkey('win', 'd')

    for i in range(2):
        if stop_flag:  # Check flag frequently
            break
        time.sleep(0.1)
        pyautogui.press('win')

# Stop the listener once the loop exits
listener.stop()
print("Program stopped.")
