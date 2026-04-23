import pyautogui
import time

def take_screenshot(path="screenshots/step1.png"):
    img = pyautogui.screenshot()
    img.save(path)
    print(f"Saved screenshot: {path}")
    return path

def locate_first_item():
    # Replace with your first-item coordinates from calibration
    first_x, first_y = 420, 365
    print(f"First item target: ({first_x}, {first_y})")
    return first_x, first_y

if __name__ == "__main__":
    time.sleep(2)
    take_screenshot()
    locate_first_item()
