import time
import json
from datetime import datetime
import pyautogui
import keyboard
import pytesseract
from PIL import ImageGrab

# Function to move the mouse in a human-like way using bezier curve
def human_like_mouse_move(start, end, duration=0.5):
    # This function will simulate a bezier curve movement from start to end
    # ... [Implementation of bezier curve movement] ...
    pyautogui.moveTo(end[0], end[1], duration)

# Function to extract text using OCR
def extract_text_from_area(region):
    # Capture the screen and apply OCR
    screen = ImageGrab.grab(bbox=region)
    text = pytesseract.image_to_string(screen)
    return text

# Function to handle the profile scraping
def scrape_linkedin_profiles():
    start_y_positions = [344, 380, 525, 670, 815]
    profile_count = len(start_y_positions)

    outputs = {}

    for index, start_y in enumerate(start_y_positions):
        profile_name_position = (242, start_y)
        arrow_button_position = (1860, start_y - 31)

        # Move and click on the profile name
        human_like_mouse_move((242, start_y - 10), profile_name_position)
        pyautogui.click(profile_name_position)

        # Open the profile in a new tab
        time.sleep(1)  # Wait for the profile to load
        human_like_mouse_move((1860, start_y - 10), arrow_button_position)
        pyautogui.click(arrow_button_position)

        # Switch to new tab
        keyboard.press_and_release('ctrl+tab')

        # Scrape profile content
        profile_texts = []
        for _ in range(10):  # Scroll 10 to 15 times
            time.sleep(5)
            profile_text = extract_text_from_area((0, 0, 1920, 1080))  # Adjust region as needed
            profile_texts.append(profile_text)
            # Scroll down
            pyautogui.scroll(-300)

        # Close the current tab
        keyboard.press_and_release('ctrl+w')

        # Save outputs
        outputs[f'profile_{index+1}'] = profile_texts
        time.sleep(random.randint(60, 600))  # Random delay between profiles

        # Check time and stop if necessary
        current_time = datetime.now()
        if current_time.weekday() > 4 or not (9 <= current_time.hour < 16 or (current_time.hour == 16 and current_time.minute <= 30)):
            print("Out of operating hours. Stopping.")
            break

    with open('Account_Outputs/profiles.json', 'w') as json_file:
        json.dump(outputs, json_file)

    # Additionally save to TXT format
    for profile_id, texts in outputs.items():
        with open(f'Account_Outputs/{profile_id}.txt', 'w') as txt_file:
            for text in texts:
                txt_file.write(text + '\n')

# Stop the script on Esc key press
keyboard.add_hotkey('esc', lambda: exit())

if __name__ == '__main__':
    scrape_linkedin_profiles()