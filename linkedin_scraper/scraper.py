"""LinkedIn Profile Scraper - Extracts text to Account_Outputs"""
import pyautogui
import time
import json
import random
from datetime import datetime
from pynput import keyboard
import logging
import os

try:
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('linkedin_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
OPERATING_HOURS = {"start": (9, 0), "end": (16, 30)}
MIN_DELAY = 60
MAX_DELAY = 600
STARTUP_DELAY = 10
SCROLL_AFTER_PROFILES = 5
OUTPUT_DIR = "Account_Outputs"

stop_scraping = False

def on_press(key):
    global stop_scraping
    if key == keyboard.Key.esc:
        logger.info("ESC pressed - stopping")
        stop_scraping = True
        return False

def is_operating_hours():
    now = datetime.now()
    if now.weekday() >= 5:
        return False
    current_time = (now.hour, now.minute)
    in_hours = OPERATING_HOURS["start"] <= current_time <= OPERATING_HOURS["end"]
    logger.info(f"Time: {now.strftime('%A %I:%M %p')} - In hours: {in_hours}")
    return in_hours

def human_mouse_move(x, y):
    current_x, current_y = pyautogui.position()
    steps = random.randint(15, 25)
    ctrl_x = (current_x + x) / 2 + random.randint(-100, 100)
    ctrl_y = (current_y + y) / 2 + random.randint(-50, 50)
    
    for i in range(steps):
        t = i / steps
        bx = (1-t)**2 * current_x + 2*(1-t)*t * ctrl_x + t**2 * x
        by = (1-t)**2 * current_y + 2*(1-t)*t * ctrl_y + t**2 * y
        pyautogui.moveTo(bx, by, duration=0.01)
        time.sleep(random.uniform(0.001, 0.01))

def extract_profile_text():
    try:
        screenshot = pyautogui.screenshot()
        
        if OCR_AVAILABLE:
            text = pytesseract.image_to_string(screenshot)
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            return {
                "timestamp": datetime.now().isoformat(),
                "text_lines": lines,
                "full_text": text
            }
        else:
            return {
                "timestamp": datetime.now().isoformat(),
                "text_lines": ["OCR not available"],
                "full_text": ""
            }
    except Exception as e:
        logger.error(f"Error: {e}")
        return None

def scrape_profile_at_position(x, y, index):
    try:
        logger.info(f"\n{'='*60}")
        logger.info(f"PROFILE {index}")
        logger.info(f"Moving to ({x}, {y})")
        
        human_mouse_move(x, y)
        time.sleep(random.uniform(0.5, 1.0))
        
        logger.info("Clicking...")
        pyautogui.click()
        
        logger.info("Loading...")
        time.sleep(random.uniform(5, 7))
        
        logger.info("Scrolling...")
        for i in range(random.randint(6, 10)):
            pyautogui.scroll(-random.randint(300, 500))
            time.sleep(random.uniform(0.8, 1.5))
        
        logger.info("Extracting text...")
        profile_data = extract_profile_text()
        
        logger.info("Going back...")
        pyautogui.press('backspace')
        time.sleep(random.uniform(3, 5))
        
        logger.info(f"✅ Profile {index} done")
        return profile_data
        
    except Exception as e:
        logger.error(f"Error: {e}")
        return None

def scroll_to_next_profiles():
    logger.info("Scrolling for more...")
    for _ in range(3):
        pyautogui.scroll(-400)
        time.sleep(random.uniform(1, 2))

def save_profiles(profiles):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    json_file = os.path.join(OUTPUT_DIR, f"linkedin_profiles_{timestamp}.json")
    txt_file = os.path.join(OUTPUT_DIR, f"linkedin_profiles_{timestamp}.txt")
    
    try:
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(profiles, f, indent=2, ensure_ascii=False)
        logger.info(f"✅ Saved: {json_file}")
        
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write(f"LinkedIn Profile Data\n")
            f.write(f"{'='*80}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total: {len(profiles)}\n")
            f.write(f"{'='*80}\n\n")
            
            for i, profile in enumerate(profiles, 1):
                f.write(f"\nPROFILE #{i}\n")
                f.write(f"{'-'*80}\n")
                if 'text_lines' in profile:
                    for line in profile['text_lines']:
                        f.write(f"{line}\n")
                f.write(f"\n{'='*80}\n")
        
        logger.info(f"✅ Saved: {txt_file}")
        
    except Exception as e:
        logger.error(f"Error saving: {e}")

def main():
    global stop_scraping
    
    logger.info("\n" + "="*60)
    logger.info("LINKEDIN SCRAPER")
    logger.info("="*60)
    logger.info(f"Output: {OUTPUT_DIR}/")
    logger.info(f"OCR: {OCR_AVAILABLE}")
    logger.info("="*60)
    
    if not is_operating_hours():
        logger.error("❌ Outside operating hours (Mon-Fri 9am-4:30pm)")
        input("Press Enter to exit...")
        exit(1)
    
    logger.info(f"\nSwitch to LinkedIn in {STARTUP_DELAY} seconds...")
    logger.info("Press ESC to stop\n")
    
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    
    for i in range(STARTUP_DELAY, 0, -1):
        print(f"{i}...", end=" ", flush=True)
        time.sleep(1)
    print("\n")
    
    logger.info("🚀 STARTING\n")
    
    all_profiles = []
    profiles_scraped = 0
    max_profiles = 50
    
    base_profile_positions = [
        (400, 280),
        (400, 405),
        (400, 555),
        (400, 680),
        (400, 800),
    ]
    
    profile_index = 0
    
    while profiles_scraped < max_profiles:
        if stop_scraping or not is_operating_hours():
            break
        
        position_index = profile_index % len(base_profile_positions)
        x, y = base_profile_positions[position_index]
        
        profile_data = scrape_profile_at_position(x, y, profiles_scraped + 1)
        
        if profile_data:
            all_profiles.append(profile_data)
            profiles_scraped += 1
            logger.info(f"Progress: {profiles_scraped}/{max_profiles}")
            
            if profiles_scraped % 5 == 0:
                save_profiles(all_profiles)
        
        profile_index += 1
        
        if profile_index % SCROLL_AFTER_PROFILES == 0:
            scroll_to_next_profiles()
        
        if profiles_scraped < max_profiles:
            delay = random.randint(MIN_DELAY, MAX_DELAY)
            logger.info(f"Waiting {delay}s ({delay/60:.1f}m)...\n")
            time.sleep(delay)
    
    save_profiles(all_profiles)
    logger.info(f"\n✅ COMPLETE! {profiles_scraped} profiles")
    logger.info(f"Saved to: {OUTPUT_DIR}/\n")
    listener.stop()

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    if not OCR_AVAILABLE:
        logger.warning("⚠️  OCR not installed - install: pip install pytesseract pillow\n")
    
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n⚠️  Stopped by user")
    except Exception as e:
        logger.error(f"\n❌ ERROR: {e}")
