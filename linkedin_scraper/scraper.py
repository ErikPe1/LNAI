"""Coordinate-driven profile workflow with screenshot + click + scroll + extract."""
import json
import logging
import os
import random
import sys
import time
from datetime import datetime
from typing import List, Tuple, Optional

import pyautogui
from pynput import keyboard

try:
    from linkedin_scraper import config
except Exception:
    import config  # fallback when running from folder directly

try:
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# ---------------- Logging ----------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(getattr(config, "LOG_FILE", "linkedin_scraper.log"), encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ---------------- Runtime flags ----------------
stop_scraping = False

# ---------------- Setup ----------------
pyautogui.FAILSAFE = getattr(config, "PYAUTOGUI_FAILSAFE", True)
pyautogui.PAUSE = getattr(config, "PYAUTOGUI_PAUSE", 0.05)

if OCR_AVAILABLE and getattr(config, "ENABLE_OCR", True):
    tcmd = getattr(config, "TESSERACT_CMD", None)
    if tcmd:
        pytesseract.pytesseract.tesseract_cmd = tcmd


def on_press(key):
    global stop_scraping
    if key == keyboard.Key.esc:
        stop_scraping = True
        logger.info("ESC pressed. Stopping...")
        return False


def is_operating_hours() -> bool:
    now = datetime.now()
    days = getattr(config, "OPERATING_HOURS", {}).get("days", [])
    if now.strftime("%A") not in days:
        return False

    start_txt = config.OPERATING_HOURS.get("start", "9:00 AM")
    end_txt = config.OPERATING_HOURS.get("end", "4:30 PM")
    start = datetime.strptime(start_txt, "%I:%M %p").time()
    end = datetime.strptime(end_txt, "%I:%M %p").time()
    return start <= now.time() <= end


def ensure_dirs():
    os.makedirs(getattr(config, "OUTPUT_DIR", "Account_Outputs"), exist_ok=True)
    os.makedirs(getattr(config, "SCREENSHOT_DIR", "screenshots"), exist_ok=True)


def take_screenshot(prefix: str = "list") -> str:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(getattr(config, "SCREENSHOT_DIR", "screenshots"), f"{prefix}_{ts}.png")
    img = pyautogui.screenshot()
    img.save(path)
    logger.info(f"Screenshot saved: {path}")
    return path


def human_mouse_move(x: int, y: int):
    current_x, current_y = pyautogui.position()
    steps = random.randint(18, 28)
    ctrl_x = (current_x + x) / 2 + random.randint(-80, 80)
    ctrl_y = (current_y + y) / 2 + random.randint(-50, 50)

    for i in range(steps):
        t = i / max(steps, 1)
        bx = (1 - t) ** 2 * current_x + 2 * (1 - t) * t * ctrl_x + t ** 2 * x
        by = (1 - t) ** 2 * current_y + 2 * (1 - t) * t * ctrl_y + t ** 2 * y
        pyautogui.moveTo(int(bx), int(by), duration=0.01)
        time.sleep(random.uniform(0.005, 0.015))


def safe_click(x: int, y: int) -> bool:
    w, h = pyautogui.size()
    if not (0 <= x < w and 0 <= y < h):
        logger.error(f"Coordinate ({x},{y}) out of bounds for screen {w}x{h}")
        return False

    retries = getattr(config, "CLICK_RETRIES", 3)
    for attempt in range(1, retries + 1):
        try:
            human_mouse_move(x, y)
            pyautogui.click(
                x=x,
                y=y,
                clicks=getattr(config, "CLICKS", 1),
                interval=getattr(config, "INTERVAL", 0.0),
                button=getattr(config, "BUTTON", "left"),
            )
            return True
        except Exception as e:
            logger.warning(f"Click attempt {attempt}/{retries} failed: {e}")
            time.sleep(0.15)
    return False


def get_profile_card_coordinates(profile_num: int) -> Tuple[int, int]:
    positions = getattr(config, "PROFILE_CARD_POSITIONS", [(420, 365)])
    idx = (profile_num - 1) % len(positions)
    return positions[idx]


def click_arrow_button() -> bool:
    x = int(getattr(config, "ARROW_BUTTON_X", 1850))
    y = int(getattr(config, "ARROW_BUTTON_Y", 311))
    logger.info(f"Clicking arrow button at ({x}, {y})")
    return safe_click(x, y)


def extract_text_from_screen() -> List[str]:
    if not OCR_AVAILABLE or not getattr(config, "ENABLE_OCR", True):
        return ["OCR unavailable/disabled"]

    try:
        img = pyautogui.screenshot()
        text = pytesseract.image_to_string(img)
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        # dedupe preserve order
        out, seen = [], set()
        for ln in lines:
            if ln not in seen:
                seen.add(ln)
                out.append(ln)
        return out
    except Exception as e:
        logger.error(f"OCR extraction error: {e}")
        return []


def scroll_profile_for_minutes(duration_minutes: float) -> List[str]:
    start = time.time()
    max_secs = duration_minutes * 60
    all_lines: List[str] = []
    scroll_count = 0

    while (time.time() - start) < max_secs and not stop_scraping:
        all_lines.extend(extract_text_from_screen())
        pyautogui.scroll(random.randint(-250, -150))
        scroll_count += 1
        time.sleep(random.uniform(10, 20))

    # dedupe
    out, seen = [], set()
    for ln in all_lines:
        if ln not in seen:
            seen.add(ln)
            out.append(ln)
    logger.info(f"Profile scrolls: {scroll_count}, lines extracted: {len(out)}")
    return out


def run_profile_cycle(profile_num: int) -> Optional[dict]:
    logger.info(f"{'='*20} PROFILE {profile_num} {'='*20}")

    # 1) screenshot list
    list_shot = take_screenshot(prefix=f"page_profile_{profile_num}")

    # 2) click profile card
    px, py = get_profile_card_coordinates(profile_num)
    logger.info(f"Clicking profile card at ({px}, {py})")
    if not safe_click(px, py):
        logger.error("Failed to click profile card.")
        return None
    time.sleep(random.uniform(1.5, 2.5))

    # 3) click arrow/open target
    if not click_arrow_button():
        logger.error("Failed to click arrow button.")
        return None
    time.sleep(random.uniform(2.0, 3.0))

    # 4) open/switch tab
    pyautogui.hotkey("ctrl", "tab")
    time.sleep(random.uniform(1.5, 2.5))

    # 5) detailed profile scroll+analysis
    dwell = random.uniform(2.0, 4.0)
    lines = scroll_profile_for_minutes(dwell)

    # 6) close and return
    pyautogui.hotkey("ctrl", "w")
    time.sleep(random.uniform(1.0, 1.8))

    return {
        "profile_number": profile_num,
        "timestamp": datetime.now().isoformat(),
        "list_screenshot": list_shot,
        "profile_click": {"x": px, "y": py},
        "arrow_click": {"x": int(getattr(config, "ARROW_BUTTON_X", 1850)), "y": int(getattr(config, "ARROW_BUTTON_Y", 311))},
        "time_spent_minutes": dwell,
        "lines_extracted": len(lines),
        "text": lines,
    }


def save_data(rows: List[dict]):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = getattr(config, "OUTPUT_DIR", "Account_Outputs")
    json_path = os.path.join(out_dir, f"profiles_{ts}.json")
    txt_path = os.path.join(out_dir, f"profiles_{ts}.txt")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(f"Run at {datetime.now().isoformat()}\n")
        f.write(f"Total profiles: {len(rows)}\n\n")
        for r in rows:
            f.write(f"PROFILE {r['profile_number']} | lines={r['lines_extracted']} | dwell={r['time_spent_minutes']:.2f}m\n")
            f.write(f"profile_click={r['profile_click']} arrow_click={r['arrow_click']}\n")
            for ln in r["text"]:
                f.write(f"{ln}\n")
            f.write("\n" + "-" * 70 + "\n\n")

    logger.info(f"Saved: {json_path}")
    logger.info(f"Saved: {txt_path}")


def main():
    ensure_dirs()

    if not is_operating_hours():
        logger.error("Outside configured operating hours.")
        return

    startup = getattr(config, "STARTUP_DELAY", 10)
    logger.info(f"Switch to target window now. Starting in {startup}s...")
    for i in range(startup, 0, -1):
        print(f"{i}...", end=" ", flush=True)
        time.sleep(1)
    print()

    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    rows: List[dict] = []
    max_profiles = 50

    for n in range(1, max_profiles + 1):
        if stop_scraping:
            break
        row = run_profile_cycle(n)
        if row:
            rows.append(row)

        # periodic save
        if n % 5 == 0 and rows:
            save_data(rows)

        # pacing
        time.sleep(random.uniform(1.0, 2.0))

    if rows:
        save_data(rows)
    listener.stop()
    logger.info("Done.")


if __name__ == "__main__":
    main()
