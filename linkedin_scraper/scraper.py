import pyautogui
import time
import json
import random
from datetime import datetime
from pynput import keyboard
import logging
import os

# Configuration Variables
OPERATING_HOURS_START = (9, 0)
OPERATING_HOURS_END = (16, 30)
MIN_DELAY = 60
MAX_DELAY = 600
STARTUP_DELAY = 10
SCROLL_AFTER_PROFILES = 5

# Function to handle ESC key
def on_press(key):
    if key == keyboard.Key.esc:
        return False

# Function to check if current time is within operating hours
def is_operating_hours():
    now = datetime.now()
    return (now.weekday() < 5) and (OPERATING_HOURS_START[0] <= now.hour < OPERATING_HOURS_END[0] or (now.hour == OPERATING_HOURS_END[0] and now.minute <= OPERATING_HOURS_END[1]))

# Function to move mouse with human-like behavior using bezier curves
def human_mouse_move(start, end, steps):
    for i in range(steps):
        interpolated_x = int(start[0] + (end[0] - start[0]) * (i / steps))
        interpolated_y = int(start[1] + (end[1] - start[1]) * (i / steps))
        pyautogui.moveTo(interpolated_x, interpolated_y)
        time.sleep(random.uniform(0.01, 0.1))

# Function to extract visible text and save it as a screenshot
def extract_visible_text():
    if not os.path.exists('data'):
        os.makedirs('data')
    screenshot_path = 'data/screenshot_{}.png'.format(int(time.time()))
    screenshot = pyautogui.screenshot()
    screenshot.save(screenshot_path)
    logging.info('Saved screenshot to {}'.format(screenshot_path))

# Function to scrape a profile at a specific position
def scrape_profile_at_position(position):
    pyautogui.click(position)
    time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))
    extract_visible_text()
    # Scroll and navigate back
    for _ in range(random.randint(6, 10)):
        pyautogui.scroll(-300)
        time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))
    pyautogui.press('backspace')

# Function to scroll to next profiles
def scroll_to_next_profiles():
    for _ in range(3):
        pyautogui.scroll(-300)
        time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))

# Function to save data to a JSON file
def save_data(data):
    with open('data/scraped_data.json', 'w') as json_file:
        json.dump(data, json_file)
    logging.info('Data saved to data/scraped_data.json')

# Main function
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    if not os.path.exists('data'):
        os.makedirs('data')
    profiles_data = []
    base_profile_positions = [(400, 280), (400, 405), (400, 555), (400, 680), (400, 800)]
    profile_count = 0
    while profile_count < 50:
        if is_operating_hours():
            for position in base_profile_positions:
                scrape_profile_at_position(position)
                profile_count += 1
                if profile_count % SCROLL_AFTER_PROFILES == 0:
                    scroll_to_next_profiles()
                if profile_count % 5 == 0:
                    save_data(profiles_data)
        else:
            logging.info('Outside of operating hours. Waiting...')
            time.sleep(60)
    save_data(profiles_data)
