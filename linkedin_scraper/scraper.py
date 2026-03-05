import time
import random
import pyautogui
import json
from pynput import keyboard

# Function to perform human-like mouse movements
def move_mouse(x, y):
    duration = random.uniform(0.5, 1.5)
    pyautogui.moveTo(x, y, duration)

# Function to click at specific coordinates
def click(x, y):
    move_mouse(x, y)
    pyautogui.click()

# Function to extract text using OCR (optical character recognition)
def extract_text_from_image(image_path):
    # Implement OCR extraction logic here
    pass  # Placeholder for OCR extraction logic

# Function to perform scraping operations
def scrape_profile():
    # Click on profile name to open side panel
    click(242, 344)
    time.sleep(random.uniform(2, 3))  # Wait for side panel to open

    # Click on arrow button to open in a new tab
    click(1860, 313)
    time.sleep(random.uniform(2, 3))  # Wait for new tab to open

    # Scroll and extract text
    for _ in range(random.randint(10, 15)):
        # Scroll down
        pyautogui.scroll(-100)
        time.sleep(random.uniform(1, 3))  # Wait for loading more content

        # Implement text extraction logic
        text = extract_text_from_image('path_to_screenshot')  # Placeholder for screenshot path
        # Save extracted text to file
        save_extracted_text(text)

    # Close the tab
    pyautogui.hotkey('ctrl', 'w')

# Function to save extracted text
def save_extracted_text(text):
    output_folder = 'Account_Outputs'
    output_file_json = f'{output_folder}/output.json'
    output_file_txt = f'{output_folder}/output.txt'

    # Remove duplicate lines
    text_lines = list(set(text.splitlines()))

    # Save to JSON
    with open(output_file_json, 'w', encoding='utf-8') as json_file:
        json.dump(text_lines, json_file, ensure_ascii=False)

    # Save to TXT
    with open(output_file_txt, 'w', encoding='utf-8') as txt_file:
        txt_file.write('\n'.join(text_lines))

# Function to start scraping
def start_scraping():
    scrape_profile()

# Add listener to stop with ESC key
listener = keyboard.Listener(on_press=lambda key: key == keyboard.Key.esc)
listener.start()
start_scraping()