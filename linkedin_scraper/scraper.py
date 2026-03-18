"""LinkedIn Sales Navigator - Accurate Profile Card Scraper"""
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
    from PIL import Image
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
STARTUP_DELAY = 10
OUTPUT_DIR = "Account_Outputs"

# CONSTANT coordinates for "open in new tab" button
NEW_TAB_BUTTON_X = 1858
NEW_TAB_BUTTON_Y = 312

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
    """Move mouse with human-like bezier curve"""
    current_x, current_y = pyautogui.position()
    steps = random.randint(20, 30)
    ctrl_x = (current_x + x) / 2 + random.randint(-100, 100)
    ctrl_y = (current_y + y) / 2 + random.randint(-50, 50)
    
    for i in range(steps):
        t = i / steps
        bx = (1-t)**2 * current_x + 2*(1-t)*t * ctrl_x + t**2 * x
        by = (1-t)**2 * current_y + 2*(1-t)*t * ctrl_y + t**2 * y
        pyautogui.moveTo(bx, by, duration=0.01)
        time.sleep(random.uniform(0.01, 0.02))

def take_screenshot():
    """Take and save screenshot"""
    try:
        screenshot = pyautogui.screenshot()
        timestamp = int(time.time())
        filename = f"{OUTPUT_DIR}/screenshot_{timestamp}.png"
        screenshot.save(filename)
        logger.info(f"Screenshot saved: {filename}")
        return screenshot
    except Exception as e:
        logger.error(f"Screenshot error: {e}")
        return None

def get_profile_card_coordinates(profile_num):
    """Return coordinates for clicking on profile cards - EXACT coordinates from screenshots"""
    
    # Exact profile card positions from provided screenshots
    profile_positions = [
        (420, 365),   # Profile 1 - Maylin Barcena
        (420, 515),   # Profile 2 - Darien Paez  
        (420, 692),   # Profile 3 - Mariela Perez
        (420, 856),   # Profile 4 - Idelvys Garcia
        (420, 931),   # Profile 5 - Maria Valentina
    ]
    
    # Cycle through positions (after 5 profiles, scroll and repeat)
    pos_index = (profile_num - 1) % len(profile_positions)
    x, y = profile_positions[pos_index]
    
    logger.info(f"Profile {profile_num} -> Position {pos_index + 1}: ({x}, {y})")
    return x, y

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

def slow_scroll_profile(duration_minutes):
    """Scroll slowly through profile for specified duration (4-8 minutes)"""
    logger.info(f"Slowly scrolling profile for {duration_minutes:.1f} minutes...")
    
    start_time = time.time()
    duration_seconds = duration_minutes * 60
    
    all_text = []
    scroll_count = 0
    
    while (time.time() - start_time) < duration_seconds:
        if stop_scraping:
            break
        
        # Extract text at current position
        text_lines = extract_full_screen()
        all_text.extend(text_lines)
        scroll_count += 1
        
        # Small scroll
        scroll_amount = random.randint(-150, -250)
        pyautogui.scroll(scroll_amount)
        
        # Wait between scrolls (15-30 seconds)
        wait_time = random.uniform(15, 30)
        elapsed = time.time() - start_time
        remaining = duration_seconds - elapsed
        
        logger.info(f"Scroll {scroll_count} | Elapsed: {elapsed/60:.1f}m | Remaining: {remaining/60:.1f}m")
        
        time.sleep(wait_time)
    
    # Remove duplicates
    unique_text = []
    seen = set()
    for line in all_text:
        if line not in seen:
            unique_text.append(line)
            seen.add(line)
    
    logger.info(f"Extracted {len(unique_text)} unique lines from profile")
    return unique_text

def slow_scroll_search_page(duration_minutes):
    """Scroll slowly on search results page (1-3 minutes)"""
    logger.info(f"Slowly scrolling search page for {duration_minutes:.1f} minutes...")
    
    start_time = time.time()
    duration_seconds = duration_minutes * 60
    
    # Focus on left side search results
    screen_width = pyautogui.size()[0]
    list_x = int(screen_width * 0.3)
    list_y = 500
    
    pyautogui.moveTo(list_x, list_y, duration=0.5)
    time.sleep(0.5)
    
    scroll_count = 0
    
    while (time.time() - start_time) < duration_seconds:
        if stop_scraping:
            break
        
        scroll_amount = random.randint(-200, -300)
        pyautogui.scroll(scroll_amount)
        scroll_count += 1
        
        wait_time = random.uniform(10, 20)
        elapsed = time.time() - start_time
        remaining = duration_seconds - elapsed
        
        logger.info(f"Search scroll {scroll_count} | Elapsed: {elapsed/60:.1f}m | Remaining: {remaining/60:.1f}m")
        
        time.sleep(wait_time)

def scrape_profile_with_screenshot(profile_num):
    """Complete workflow: screenshot → click card → open tab → scrape → close"""
    try:
        logger.info(f"\n{'='*60}")
        logger.info(f"PROFILE {profile_num}")
        logger.info(f"{'='*60}")
        
        # Step 1: Take screenshot
        logger.info("Step 1: Taking screenshot...")
        screenshot = take_screenshot()
        
        # Get EXACT coordinates for this profile card
        profile_x, profile_y = get_profile_card_coordinates(profile_num)
        
        # Step 2: Click profile card
        logger.info("Step 2: Clicking profile card...")
        human_mouse_move(profile_x, profile_y)
        time.sleep(random.uniform(0.5, 1.0))
        pyautogui.click()
        time.sleep(random.uniform(2, 3))
        
        # Step 3: Click "open in new tab" at CONSTANT coordinates
        logger.info(f"Step 3: Opening in new tab at ({NEW_TAB_BUTTON_X}, {NEW_TAB_BUTTON_Y})...")
        human_mouse_move(NEW_TAB_BUTTON_X, NEW_TAB_BUTTON_Y)
        time.sleep(random.uniform(0.3, 0.5))
        pyautogui.click()
        
        # Step 4: Wait for tab to load
        logger.info("Step 4: Waiting for new tab...")
        time.sleep(random.uniform(3, 5))
        
        # Step 5: Switch to new tab
        logger.info("Step 5: Switching to new tab...")
        pyautogui.hotkey('ctrl', 'tab')
        time.sleep(random.uniform(2, 3))
        
        # Step 6: Slowly scroll profile (4-8 minutes)
        profile_duration = random.uniform(4, 8)
        logger.info(f"Step 6: Scrolling profile for {profile_duration:.1f} minutes...")
        profile_text = slow_scroll_profile(profile_duration)
        
        profile_data = {
            "profile_number": profile_num,
            "timestamp": datetime.now().isoformat(),
            "click_coordinates": {"x": profile_x, "y": profile_y},
            "text": profile_text,
            "total_lines": len(profile_text),
            "time_spent_minutes": profile_duration
        }
        
        # Step 7: Close tab
        logger.info("Step 7: Closing tab...")
        pyautogui.hotkey('ctrl', 'w')
        time.sleep(random.uniform(1, 2))
        
        # Step 8: Slowly scroll search page (1-3 minutes)
        search_duration = random.uniform(1, 3)
        logger.info(f"Step 8: Scrolling search page for {search_duration:.1f} minutes...")
        slow_scroll_search_page(search_duration)
        
        logger.info(f"[OK] Profile {profile_num} complete! ({len(profile_text)} lines)")
        return profile_data
        
    except Exception as e:
        logger.error(f"Error on profile {profile_num}: {e}")
        try:
            pyautogui.hotkey('ctrl', 'w')
            time.sleep(1)
        except:
            pass
        return None

def save_data(profiles):
    """Save profiles to JSON and TXT"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_file = f"{OUTPUT_DIR}/profiles_{timestamp}.json"
    txt_file = f"{OUTPUT_DIR}/profiles_{timestamp}.txt"
    
    try:
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(profiles, f, indent=2, ensure_ascii=False)
        logger.info(f"[OK] JSON: {json_file}")
        
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write(f"LinkedIn Profiles - Slow Scroll Extraction\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Profiles: {len(profiles)}\n")
            f.write("="*80 + "\n\n")
            
            for p in profiles:
                f.write(f"PROFILE {p.get('profile_number')}\n")
                f.write(f"Timestamp: {p.get('timestamp')}\n")
                f.write(f"Coordinates: {p.get('click_coordinates')}\n")
                f.write(f"Time Spent: {p.get('time_spent_minutes', 0):.1f} minutes\n")
                f.write(f"Lines Extracted: {p.get('total_lines', 0)}\n")
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
    logger.info("LinkedIn Sales Navigator - Exact Coordinates Scraper")
    logger.info("="*60)
    logger.info(f"Switch to LinkedIn in {STARTUP_DELAY}s")
    logger.info("Press ESC to stop")
    logger.info(f"New Tab Button: ({NEW_TAB_BUTTON_X}, {NEW_TAB_BUTTON_Y})")
    logger.info("Profile scroll: 4-8 min | Search scroll: 1-3 min")
    logger.info("="*60)
    
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    
    for i in range(STARTUP_DELAY, 0, -1):
        print(f"{i}...", end=" ", flush=True)
        time.sleep(1)
    print("\n")
    
    profiles = []
    profile_count = 0
    max_profiles = 50
    
    while profile_count < max_profiles:
        if stop_scraping or not is_operating_hours():
            break
        
        profile_count += 1
        data = scrape_profile_with_screenshot(profile_count)
        
        if data:
            profiles.append(data)
            logger.info(f"[OK] {profile_count}/{max_profiles} profiles completed")
            
            # Save every 5 profiles
            if profile_count % 5 == 0:
                save_data(profiles)
                logger.info(f"[CHECKPOINT] Saved {profile_count} profiles")
    
    # Final save
    save_data(profiles)
    logger.info(f"\n[DONE] {profile_count} profiles saved to {OUTPUT_DIR}/")
    listener.stop()

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    if not OCR_AVAILABLE:
        logger.warning("WARNING: OCR not installed - limited text extraction")
        logger.warning("Install with: pip install pytesseract pillow")
    
    if not is_operating_hours():
        logger.error("Not within operating hours (Mon-Fri, 9am-4:30pm)")
        exit(1)
    
    main()
