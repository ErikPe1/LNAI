"""
Configuration settings for LinkedIn Profile Scraper
"""

import os
import pytz

# Operating hours configuration
OPERATING_HOURS = {
    "start_hour": 9,  # 9:00 AM
    "start_minute": 0,
    "end_hour": 16,  # 4:00 PM
    "end_minute": 30,  # 4:30 PM
}

# Operating days (Monday=0, Sunday=6)
OPERATING_DAYS = [0, 1, 2, 3, 4]  # Monday through Friday

# Delay configuration (in seconds)
MIN_DELAY = 60  # 1 minute
MAX_DELAY = 600  # 10 minutes

# Short delays for page interactions (in seconds)
SCROLL_DELAY_MIN = 1
SCROLL_DELAY_MAX = 3
CLICK_DELAY_MIN = 2
CLICK_DELAY_MAX = 4

# Time zone
TIMEZONE = pytz.timezone("America/New_York")  # Default to Eastern Time

# LinkedIn URLs
LINKEDIN_BASE_URL = "https://www.linkedin.com"
LINKEDIN_LOGIN_URL = f"{LINKEDIN_BASE_URL}/login"

# Selenium configuration
HEADLESS_MODE = False  # Set to True to run browser in headless mode
IMPLICIT_WAIT = 10  # Seconds to wait for elements

# Data storage
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
OUTPUT_FILE = "linkedin_profiles.csv"
JSON_OUTPUT_FILE = "linkedin_profiles.json"

# Logging configuration
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_LEVEL = "INFO"
LOG_FILE = "linkedin_scraper.log"
