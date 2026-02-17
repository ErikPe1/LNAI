"""
Main LinkedIn Profile Scraper class
"""

import logging
import os
import time
import random
import json
import csv
from typing import List, Optional, Set
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

from . import config
from .scheduler import is_within_operating_hours, log_time_constraint_stop, get_current_time_info
from .profile_extractor import extract_profile_data

logger = logging.getLogger(__name__)


class LinkedInScraper:
    """
    Automated LinkedIn profile scraper with intelligent scheduling.
    """
    
    def __init__(self, email: Optional[str] = None, password: Optional[str] = None):
        """
        Initialize the LinkedIn scraper.
        
        Args:
            email: LinkedIn email (or loaded from LINKEDIN_EMAIL env var)
            password: LinkedIn password (or loaded from LINKEDIN_PASSWORD env var)
        """
        self.email = email or os.getenv("LINKEDIN_EMAIL")
        self.password = password or os.getenv("LINKEDIN_PASSWORD")
        
        if not self.email or not self.password:
            raise ValueError(
                "LinkedIn credentials not provided. "
                "Either pass them to __init__ or set LINKEDIN_EMAIL and LINKEDIN_PASSWORD env vars."
            )
        
        self.driver = None
        self.scraped_urls: Set[str] = set()
        self._setup_logging()
        self._setup_data_directory()
    
    def _setup_logging(self):
        """Configure logging for the scraper."""
        logging.basicConfig(
            level=getattr(logging, config.LOG_LEVEL),
            format=config.LOG_FORMAT,
            handlers=[
                logging.FileHandler(config.LOG_FILE),
                logging.StreamHandler()
            ]
        )
        logger.info("LinkedIn Scraper initialized")
    
    def _setup_data_directory(self):
        """Ensure data directory exists."""
        Path(config.DATA_DIR).mkdir(parents=True, exist_ok=True)
        logger.debug(f"Data directory: {config.DATA_DIR}")
    
    def _init_driver(self):
        """Initialize Selenium WebDriver."""
        logger.info("Initializing Chrome WebDriver")
        
        chrome_options = Options()
        if config.HEADLESS_MODE:
            chrome_options.add_argument("--headless")
        
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        
        # Set user agent
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.implicitly_wait(config.IMPLICIT_WAIT)
        
        logger.info("WebDriver initialized successfully")
    
    def login(self):
        """
        Log in to LinkedIn.
        """
        if not self.driver:
            self._init_driver()
        
        logger.info("Logging in to LinkedIn")
        
        try:
            self.driver.get(config.LINKEDIN_LOGIN_URL)
            time.sleep(random.uniform(2, 4))
            
            # Enter email
            email_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            email_field.send_keys(self.email)
            time.sleep(random.uniform(0.5, 1.5))
            
            # Enter password
            password_field = self.driver.find_element(By.ID, "password")
            password_field.send_keys(self.password)
            time.sleep(random.uniform(0.5, 1.5))
            
            # Click sign in
            sign_in_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            sign_in_button.click()
            
            # Wait for login to complete
            time.sleep(random.uniform(3, 5))
            
            # Check if login was successful
            if "feed" in self.driver.current_url or "mynetwork" in self.driver.current_url:
                logger.info("Successfully logged in to LinkedIn")
            else:
                logger.warning("Login may have failed - unexpected URL after login")
        
        except Exception as e:
            logger.error(f"Error during login: {e}")
            raise
    
    def _random_delay(self):
        """
        Apply random delay between profile scrapes.
        """
        delay = random.randint(config.MIN_DELAY, config.MAX_DELAY)
        logger.info(f"Waiting {delay} seconds before next profile...")
        time.sleep(delay)
    
    def _short_delay(self, min_sec: float = None, max_sec: float = None):
        """
        Apply short random delay for page interactions.
        
        Args:
            min_sec: Minimum delay in seconds
            max_sec: Maximum delay in seconds
        """
        min_delay = min_sec or config.CLICK_DELAY_MIN
        max_delay = max_sec or config.CLICK_DELAY_MAX
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
    def _get_profile_links(self, search_url: str) -> List[str]:
        """
        Extract profile links from search results or feed.
        
        Args:
            search_url: LinkedIn search URL or feed URL
            
        Returns:
            List of profile URLs
        """
        logger.info(f"Navigating to: {search_url}")
        self.driver.get(search_url)
        self._short_delay(2, 4)
        
        # Scroll to load more results
        for _ in range(3):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            self._short_delay(1, 2)
        
        # Find profile links
        profile_links = []
        try:
            # Try different selectors for profile links
            link_elements = self.driver.find_elements(
                By.CSS_SELECTOR,
                "a[href*='/in/']"
            )
            
            for element in link_elements:
                href = element.get_attribute("href")
                if href and "/in/" in href and href not in profile_links:
                    # Clean URL (remove query parameters)
                    clean_url = href.split("?")[0]
                    if clean_url not in self.scraped_urls:
                        profile_links.append(clean_url)
            
            logger.info(f"Found {len(profile_links)} profile links")
        except Exception as e:
            logger.error(f"Error extracting profile links: {e}")
        
        return profile_links
    
    def _save_profile_data(self, profile_data: dict):
        """
        Save profile data to CSV and JSON files.
        
        Args:
            profile_data: Profile data dictionary
        """
        # Save to JSON
        json_file = os.path.join(config.DATA_DIR, config.JSON_OUTPUT_FILE)
        try:
            # Load existing data
            if os.path.exists(json_file):
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = []
            
            # Append new profile
            data.append(profile_data)
            
            # Save back
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Saved profile data to {json_file}")
        except Exception as e:
            logger.error(f"Error saving to JSON: {e}")
        
        # Save to CSV (flattened data)
        csv_file = os.path.join(config.DATA_DIR, config.OUTPUT_FILE)
        try:
            # Flatten data for CSV
            flat_data = {
                "scraped_at": profile_data.get("scraped_at", ""),
                "name": profile_data.get("name", ""),
                "headline": profile_data.get("headline", ""),
                "location": profile_data.get("location", ""),
                "profile_url": profile_data.get("profile_url", ""),
                "about": profile_data.get("about", ""),
                "num_experiences": len(profile_data.get("experience", [])),
                "num_education": len(profile_data.get("education", [])),
                "num_skills": len(profile_data.get("skills", [])),
            }
            
            file_exists = os.path.exists(csv_file)
            with open(csv_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=flat_data.keys())
                if not file_exists:
                    writer.writeheader()
                writer.writerow(flat_data)
            
            logger.debug(f"Saved profile data to {csv_file}")
        except Exception as e:
            logger.error(f"Error saving to CSV: {e}")
    
    def scrape_profile(self, profile_url: str) -> Optional[dict]:
        """
        Scrape a single LinkedIn profile.
        
        Args:
            profile_url: URL of the LinkedIn profile
            
        Returns:
            Profile data dictionary or None if failed
        """
        if profile_url in self.scraped_urls:
            logger.info(f"Profile already scraped: {profile_url}")
            return None
        
        logger.info(f"Scraping profile: {profile_url}")
        
        try:
            self.driver.get(profile_url)
            self._short_delay(3, 5)
            
            # Extract profile data
            profile_data = extract_profile_data(self.driver)
            
            # Save data
            self._save_profile_data(profile_data)
            
            # Mark as scraped
            self.scraped_urls.add(profile_url)
            
            logger.info(f"Successfully scraped profile: {profile_data.get('name', 'Unknown')}")
            return profile_data
        
        except Exception as e:
            logger.error(f"Error scraping profile {profile_url}: {e}")
            return None
    
    def scrape_profiles(self, search_url: str, max_profiles: int = 50):
        """
        Scrape multiple profiles from a search URL or feed.
        
        Args:
            search_url: LinkedIn search URL or feed URL
            max_profiles: Maximum number of profiles to scrape
        """
        logger.info(f"Starting profile scraping session")
        logger.info(f"Search URL: {search_url}")
        logger.info(f"Max profiles: {max_profiles}")
        
        if not self.driver:
            self.login()
        
        profiles_scraped = 0
        
        # Get all profile links upfront
        logger.info("Collecting profile links from search results...")
        profile_links = self._get_profile_links(search_url)
        
        if not profile_links:
            logger.warning("No profile links found")
            return
        
        logger.info(f"Found {len(profile_links)} profile links to scrape")
        
        # Scrape each profile
        for profile_url in profile_links:
            if profiles_scraped >= max_profiles:
                logger.info(f"Reached maximum profiles limit: {max_profiles}")
                break
            
            # Check operating hours before each profile
            if not is_within_operating_hours():
                log_time_constraint_stop()
                break
            
            # Scrape profile
            result = self.scrape_profile(profile_url)
            
            if result:
                profiles_scraped += 1
                logger.info(f"Progress: {profiles_scraped}/{max_profiles} profiles scraped")
            
            # Random delay before next profile (but not after the last one)
            if profiles_scraped < max_profiles and profiles_scraped < len(profile_links):
                self._random_delay()
        
        logger.info(f"Scraping session completed. Total profiles scraped: {profiles_scraped}")
    
    def close(self):
        """Close the browser and clean up."""
        if self.driver:
            logger.info("Closing browser")
            self.driver.quit()
            self.driver = None
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
