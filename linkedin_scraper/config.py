"""
Configuration settings for LinkedIn Profile Scraper.
"""
import os

# Operating hours (24-hour format)
OPERATING_START_HOUR = 9  # 9:00 AM
OPERATING_START_MINUTE = 0
OPERATING_END_HOUR = 16  # 4:30 PM
OPERATING_END_MINUTE = 30

# Operating days (0=Monday, 6=Sunday)
OPERATING_DAYS = [0, 1, 2, 3, 4]  # Monday to Friday

# Delay settings (in seconds)
MIN_DELAY = 60  # 1 minute
MAX_DELAY = 600  # 10 minutes

# Shorter delays for page interactions (in seconds)
SCROLL_DELAY_MIN = 1
SCROLL_DELAY_MAX = 3
CLICK_DELAY_MIN = 2
CLICK_DELAY_MAX = 5

# Time zone (default to system timezone)
TIMEZONE = os.getenv('TIMEZONE', 'UTC')

# LinkedIn URLs
LINKEDIN_LOGIN_URL = "https://www.linkedin.com/login"
LINKEDIN_FEED_URL = "https://www.linkedin.com/feed/"

# Data storage
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
PROFILES_JSON = os.path.join(DATA_DIR, 'profiles.json')
PROFILES_CSV = os.path.join(DATA_DIR, 'profiles.csv')
SCRAPED_URLS_FILE = os.path.join(DATA_DIR, 'scraped_urls.txt')

# Browser settings
HEADLESS_MODE = os.getenv('HEADLESS_MODE', 'False').lower() == 'true'
BROWSER_TIMEOUT = 30

# Logging
LOG_FILE = os.path.join(DATA_DIR, 'scraper.log')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
