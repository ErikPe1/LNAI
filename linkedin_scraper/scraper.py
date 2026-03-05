"""LinkedIn Sales Navigator - Full Profile Scraper (Fixed)"""
import pyautogui
import time
import json
import random
from datetime import datetime
from pynput import keyboard
import logging
import os
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

try:
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('linkedin_scraper.log', encoding='utf-8'),
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

def extract_full_screen():
    """Extract text from entire screen"""
    try:
        screenshot = pyautogui.screenshot()
        
        if OCR_AVAILABLE:
            text = pytesseract.image_to_string(screenshot)
            lines = [l.strip() for l in text.split('\n') if l.strip()]
            return lines
        else:
            return ["OCR unavailable"]
    except Exception as e:
        logger.error(f"Extract error: {e}")
        return []

def scrape_profile_full_page(profile_name_y, arrow_y, index):
    """Click profile, click arrow to open new tab, scrape, close tab"""
    try:
        # STEP 1: Click profile name to open side panel
        profile_x = 242
        logger.info(f"Profile {index}: Clicking profile name at ({profile_x}, {profile_name_y})")
        human_mouse_move(profile_x, profile_name_y)
        time.sleep(random.uniform(0.5, 0.8))
        pyautogui.click()
        time.sleep(random.uniform(2, 3))  # Wait for side panel to open
        
        # STEP 2: Click arrow button to open in new tab
        arrow_x = 1860
        logger.info(f"Profile {index}: Clicking arrow at ({arrow_x}, {arrow_y})")
        human_mouse_move(arrow_x, arrow_y)
        time.sleep(random.uniform(0.5, 0.8))
        pyautogui.click()
        
        # STEP 3: Wait for new tab to open (NO Ctrl+Tab!)
        logger.info(f"Profile {index}: Waiting for new tab to open...")
        time.sleep(random.uniform(4, 5))  # Longer wait for tab to open and load
        
        # STEP 4: Now we're on the profile page - scroll and extract
        logger.info(f"Profile {index}: Starting extraction...")
        
        all_text = []
        scroll_count = random.randint(10, 15)
        
        for scroll_num in range(scroll_count):
            logger.info(f"Profile {index}: Scroll {scroll_num + 1}/{scroll_count}")
            
            # Extract text at current position
            text_lines = extract_full_screen()
            all_text.extend(text_lines)
            
            # Scroll down
            pyautogui.scroll(-random.randint(300, 500))
            time.sleep(random.uniform(1.5, 2.0))
        
        # Final extraction
        logger.info(f"Profile {index}: Final extraction...")
        final_text = extract_full_screen()
        all_text.extend(final_text)
        
        # Remove duplicates
        unique_text = []
        seen = set()
        for line in all_text:
            if line not in seen:
                unique_text.append(line)
                seen.add(line)
        
        profile_data = {
            "timestamp": datetime.now().isoformat(),
            "text": unique_text,
            "total_lines": len(unique_text)
        }
        
        # STEP 5: Close the tab
        logger.info(f"Profile {index}: Closing tab...")
        pyautogui.hotkey('ctrl', 'w')
        time.sleep(random.uniform(2, 3))
        
        logger.info(f"Profile {index}: Complete! Extracted {len(unique_text)} lines")
        
        return profile_data
        
    except Exception as e:
        logger.error(f"Error: {e}")
        try:
            pyautogui.hotkey('ctrl', 'w')
            time.sleep(1)
        except:
            pass
        return None

def scroll_main_list():
    """Scroll search results list"""
    logger.info("Scrolling main list...")
    pyautogui.moveTo(500, 400, duration=0.5)
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
        logger.info(f"[OK] JSON: {json_file}")
        
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write(f"LinkedIn Profiles - Full Extraction\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total: {len(profiles)}\n")
            f.write("="*80 + "\n\n")
            
            for i, p in enumerate(profiles, 1):
                f.write(f"PROFILE {i}\n")
                f.write(f"Time: {p.get('timestamp')}\n")
                f.write(f"Lines: {p.get('total_lines', 0)}\n")
                f.write("-"*80 + "\n")
                
                for line in p.get('text', []):
                    f.write(f"{line}\n")
                
                f.write("\n" + "="*80 + "\n\n")
        
        logger.info(f"[OK] TXT: {txt_file}")
    except Exception as e:
        logger.error(f"Save error: {e}")

def main():
    global stop_scraping
    
    logger.info("="*60)
    logger.info("LinkedIn Sales Navigator - Full Profile Scraper")
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
    
    # Profile positions based on your exact coordinates
    # profile_name_y, arrow_y (arrow is 31 pixels above name)
    profile_positions = [
        {"name_y": 344, "arrow_y": 313},   # First profile
        {"name_y": 444, "arrow_y": 413},   # Profile 2
        {"name_y": 544, "arrow_y": 513},   # Profile 3
        {"name_y": 644, "arrow_y": 613},   # Profile 4
        {"name_y": 744, "arrow_y": 713},   # Profile 5
    ]
    
    idx = 0
    
    while count < max_profiles:
        if stop_scraping or not is_operating_hours():
            break
        
        pos_idx = idx % len(profile_positions)
        pos = profile_positions[pos_idx]
        
        data = scrape_profile_full_page(pos["name_y"], pos["arrow_y"], count + 1)
        
        if data:
            profiles.append(data)
            count += 1
            logger.info(f"[OK] {count}/{max_profiles} - {data.get('total_lines', 0)} lines")
            
            if count % 5 == 0:
                save_data(profiles)
        
        idx += 1
        
        if idx % 5 == 0:
            scroll_main_list()
        
        if count < max_profiles:
            delay = random.randint(MIN_DELAY, MAX_DELAY)
            logger.info(f"[WAIT] {delay}s ({delay/60:.1f}m)")
            time.sleep(delay)
    
    save_data(profiles)
    logger.info(f"[DONE] {count} profiles -> {OUTPUT_DIR}/")
    listener.stop()

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    if not OCR_AVAILABLE:
        logger.warning("Install OCR: pip install pytesseract pillow")
    if not is_operating_hours():
        logger.error("Not within hours (Mon-Fri 9am-4:30pm)")
        exit(1)
    main()
