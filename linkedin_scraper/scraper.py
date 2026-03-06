import time
import json
import random
import pytz
import datetime
import pyautogui
import cv2
from PIL import Image
import pytesseract

# Define the coordinates for profile name and arrow button
PROFILE_X = 424
PROFILE_Y_POSITIONS = [344, 444, 544, 644, 744]
ARROW_X = 1860
ARROW_Y = 313

# Operating hours
START_HOUR = 9  # 9 AM
END_HOUR = 16  # 4 PM
END_MINUTE = 30  # 4:30 PM

# Function to check if the current time is within operating hours
def within_operating_hours():
    now = datetime.datetime.now(pytz.utc).astimezone(pytz.timezone('America/New_York'))  # Adjust timezone as necessary
    return (now.weekday() < 5) and (START_HOUR <= now.hour < END_HOUR or (now.hour == END_HOUR and now.minute <= END_MINUTE))

# Function to perform a human-like mouse movement
def human_like_move(x, y):
    current_x, current_y = pyautogui.position()
    transition_steps = 10
    for i in range(transition_steps + 1):
        delta_x = (x - current_x) * i // transition_steps
        delta_y = (y - current_y) * i // transition_steps
        pyautogui.moveTo(current_x + delta_x, current_y + delta_y)
        time.sleep(random.uniform(0.05, 0.15))  # random delay between movements

# Main scraper function
def run_scraper():
    # Check for operating hours
    if not within_operating_hours():
        print("Outside operating hours. Exiting.")
        return

    seen_profiles = set()
    profile_data = []

    for position in PROFILE_Y_POSITIONS:
        human_like_move(PROFILE_X, position)
        pyautogui.click()  # Click on profile name
        time.sleep(random.uniform(2, 5))  # Wait for the profile to load

        human_like_move(ARROW_X, ARROW_Y)
        pyautogui.click()  # Click on arrow button to open new tab
        time.sleep(random.uniform(2, 5))  # Allow time for the new tab to load

        # Scrolling and extracting text
        for _ in range(random.randint(10, 15)):
            # Screenshot to extract text
            screen = pyautogui.screenshot()
            screen = cv2.cvtColor(numpy.array(screen), cv2.COLOR_RGB2BGR)
            text = pytesseract.image_to_string(screen)

            if text.strip():
                seen_profiles.add(text.strip())
                profile_data.append(text.strip())

            # Scroll down
            pyautogui.scroll(-100)
            time.sleep(random.uniform(0.5, 1.5))  # Random delay between scrolling

        pyautogui.hotkey('ctrl', 'w')  # Close tab
        time.sleep(random.uniform(1, 3))  # Wait for closing tab

    # Save results to files
    with open('Account_Outputs/profile_data.json', 'w') as json_file:
        json.dump(list(seen_profiles), json_file, indent=4)
    with open('Account_Outputs/profile_data.txt', 'w') as txt_file:
        txt_file.write('\n'.join(list(seen_profiles)))

# Start the scraper
if __name__ == '__main__':
    run_scraper()
