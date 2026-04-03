import pyautogui
import time

print("Moving to first profile in 3 seconds...")
time.sleep(3)
pyautogui.moveTo(360, 365, duration=1)
print("Is the mouse on Maylin Barcena's name? (y/n)")
