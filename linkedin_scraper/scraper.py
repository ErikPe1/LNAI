"""LinkedIn Sales Navigator - Right Panel Profile Scraper"""
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

OPERATING_HOURS = {"start": (9, 0), "end": (16, 30)}
MIN_DELAY = 60
MAX_DELAY = 600
STARTUP_DELAY = 10
OUTPUT_DIR = "Account_Outputs"

stop_scraping = False

def on_press(key):
    global stop_scraping
    if key == keyboard.Key.esc:
        logger.info("ESC - stopping")
        stop_scraping = True
        return False

def is_operating_hours():
    now = datetime.now()
    return now.weekday() < 5 and OPERATING_HOURS["start"] <= (now.hour, now.minute) <= OPERATING_HOURS["end"]

def human_mouse_move(x, y):
    current_x, current_y = pyautogui.position()
    steps = random.randint(15, 25)
    ctrl_x = (current_x + x) / 2 + random.randint(-50, 50)
    ctrl_y = (current_y + y) / 2 + random.randint(-30, 30)
    
    for i in range(steps):
        t = i / steps
        bx = (1-t)**2 * current_x + 2*(1-t)*t * ctrl_x + t**2 * x
        by = (1-t)**2 * current_y + 2*(1-t)*t * ctrl_y + t**2 * y
        pyautogui.moveTo(bx, by, duration=0.01)
        time.sleep(random.uniform(0.001, 0.01))

def extract_right_panel():
    """Extract text from right panel only"""
    try:
        screenshot = pyautogui.screenshot()
        screen_width, screen_height = pyautogui.size()
        
        # Right panel starts at ~70% of screen width
        right_x = int(screen_width * 0.7)
        right_panel = screenshot.crop((right_x, 0, screen_width, screen_height))
        
        if OCR_AVAILABLE:
            text = pytesseract.image_to_string(right_panel)
            lines = [l.strip() for l in text.split('\n') if l.strip()]
            logger.info(f"Extracted {len(lines)} lines")
            return {"timestamp": datetime.now().isoformat(), "text": lines}
        else:
            return {"timestamp": datetime.now().isoformat(), "text": ["OCR unavailable"]}
    except Exception as e:
        logger.error(f"Extract error: {e}")
        return None

def scroll_right_panel():
    """Scroll the right panel"""
    screen_width = pyautogui.size()[0]
    panel_x = int(screen_width * 0.85)
    panel_y = 400
    
    logger.info("Scrolling right panel...")
    pyautogui.moveTo(panel_x, panel_y, duration=0.5)
    time.sleep(0.5)
    
    for i in range(random.randint(8, 12)):
        pyautogui.scroll(random.randint(-300, -500))
        time.sleep(random.uniform(0.8, 1.5))

def close_panel():
    """Close right panel - click X button"""
    screen_width = pyautogui.size()[0]
    close_x = int(screen_width * 0.98)  # X button at far right
    close_y = 247  # Based on your screenshot
    
    logger.info("Closing panel...")
    human_mouse_move(close_x, close_y)
    time.sleep(0.3)
    pyautogui.click()
    time.sleep(random.uniform(1, 2))

def scrape_profile(x, y, index):
    try:
        logger.info(f"Profile {index}: Click at ({x}, {y})")
        human_mouse_move(x, y)
        time.sleep(random.uniform(0.5, 1.0))
        pyautogui.click()
        
        logger.info(f"Profile {index}: Panel loading...")
        time.sleep(random.uniform(3, 5))
        
        scroll_right_panel()
        
        logger.info(f"Profile {index}: Extracting...")
        data = extract_right_panel()
        
        close_panel()
        
        return data
    except Exception as e:
        logger.error(f"Error: {e}")
        return None

def scroll_main_list():
    """Scroll main results list"""
    logger.info("Scrolling main list...")
    screen_width = pyautogui.size()[0]
    list_x = int(screen_width * 0.4)
    
    pyautogui.moveTo(list_x, 400, duration=0.5)
    time.sleep(0.5)
    
    for _ in range(3):
        pyautogui.scroll(-400)
        time.sleep(random.uniform(1, 2))

def save_data(profiles):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_file = f"{OUTPUT_DIR}/profiles_{timestamp}.json"
    txt_file = f"{OUTPUT_DIR}/profiles_{timestamp}.txt"
    
    try:
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(profiles, f, indent=2, ensure_ascii=False)
        logger.info(f"✅ JSON: {json_file}")
        
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write(f"LinkedIn Profiles\n{datetime.now()}\nTotal: {len(profiles)}\n{'='*80}\n\n")
            for i, p in enumerate(profiles, 1):
                f.write(f"PROFILE {i}\n{p.get('timestamp')}\n{'-'*80}\n")
                for line in p.get('text', []):
                    f.write(f"{line}\n")
                f.write(f"\n{'='*80}\n\n")
        logger.info(f"✅ TXT: {txt_file}")
    except Exception as e:
        logger.error(f"Save error: {e}")

def main():
    global stop_scraping
    
    logger.info("="*60)
    logger.info("LinkedIn Sales Navigator Scraper")
    logger.info("="*60)
    logger.info(f"Switch to LinkedIn in {STARTUP_DELAY}s")
    logger.info("Press ESC to stop")
    logger.info("="*60)
    
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    
    for i in range(STARTUP_DELAY, 0, -1):
        print(f"{i}...", end=" ", flush=True)
        time.sleep(1)
    print("\n")
    
    profiles = []
    count = 0
    max_profiles = 50
    
    # Profile name positions (left side list)
    positions = [
        (800, 349),   # Maylin Barcena
        (422, 512),   # Darien Paez
        (422, 675),   # Mariela Perez
        (422, 838),   # Idelvys Garcia
        (422, 1001),   # Maria Valentina
    ]
    
    idx = 0
    
    while count < max_profiles:
        if stop_scraping or not is_operating_hours():
            break
        
        pos_idx = idx % len(positions)
        x, y = positions[pos_idx]
        
        data = scrape_profile(x, y, count + 1)
        
        if data:
            profiles.append(data)
            count += 1
            logger.info(f"✅ Scraped {count}/{max_profiles}")
            
            if count % 5 == 0:
                save_data(profiles)
        
        idx += 1
        
        if idx % 5 == 0:
            scroll_main_list()
        
        if count < max_profiles:
            delay = random.randint(MIN_DELAY, MAX_DELAY)
            logger.info(f"⏳ Waiting {delay}s...")
            time.sleep(delay)
    
    save_data(profiles)
    logger.info(f"✅ Done! {count} profiles → {OUTPUT_DIR}/")
    listener.stop()

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    if not OCR_AVAILABLE:
        logger.warning("Install OCR: pip install pytesseract pillow")
    if not is_operating_hours():
        logger.error("Not within hours (Mon-Fri 9am-4:30pm)")
        exit(1)
    main()
