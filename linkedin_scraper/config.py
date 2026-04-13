# Configuration settings for automation

# Operating hours (local time)
OPERATING_HOURS = {
    "start": "9:00 AM",
    "end": "4:30 PM",
    "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
}

# Delay settings
MIN_DELAY = 60  # seconds
MAX_DELAY = 600  # seconds

# Data directory
DATA_DIRECTORY = "data"

# Startup delay
STARTUP_DELAY = 10  # seconds

# Mouse movement speed settings
MOUSE_MOVEMENT_SPEED = "natural"

# --- NEW: Coordinate-driven click configuration ---
# Small arrow-box target coordinates
ARROW_BUTTON_X = 1850
ARROW_BUTTON_Y = 311

# Click behavior
MOVE_DURATION = 0.10
CLICKS = 1
INTERVAL = 0.0
BUTTON = "left"
CLICK_RETRIES = 3

# Optional profile card coordinates (fallback/manual mode)
PROFILE_CARD_POSITIONS = [
    (420, 365),
    (420, 515),
    (420, 692),
    (420, 856),
    (420, 931),
]

# OCR
ENABLE_OCR = True
TESSERACT_CMD = None  # Example: r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Output folders/files
OUTPUT_DIR = "Account_Outputs"
SCREENSHOT_DIR = "screenshots"
LOG_FILE = "linkedin_scraper.log"

# Safety
PYAUTOGUI_FAILSAFE = True
PYAUTOGUI_PAUSE = 0.05
