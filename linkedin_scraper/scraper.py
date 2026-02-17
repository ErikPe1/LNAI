"""
Main LinkedIn profile scraper logic.
Handles authentication, navigation, and orchestration of profile scraping.
"""
import logging
import time
import random
import json
import csv
import os
from typing import List, Dict, Any, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv

from . import config
from .scheduler import should_continue_scraping, get_current_time
from .profile_extractor import extract_profile_data

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class LinkedInScraper:
    """
    LinkedIn profile scraper with intelligent scheduling and data extraction.
    """
    
    def __init__(self, headless: bool = None):
        """
        Initialize the scraper.
        
        Args:
            headless: Run browser in headless mode (default from config)
        """
        self.driver = None
        self.headless = headless if headless is not None else config.HEADLESS_MODE
        self.scraped_urls = self._load_scraped_urls()
        logger.info("LinkedInScraper initialized")
    
    def _load_scraped_urls(self) -> set:
        """
        Load previously scraped URLs from file.
        
        Returns:
            Set of already-scraped URLs
        """
        if os.path.exists(config.SCRAPED_URLS_FILE):
            try:
                with open(config.SCRAPED_URLS_FILE, 'r') as f:
                    urls = set(line.strip() for line in f if line.strip())
                logger.info(f"Loaded {len(urls)} previously scraped URLs")
                return urls
            except Exception as e:
                logger.error(f"Error loading scraped URLs: {e}")
        return set()
    
    def _save_scraped_url(self, url: str):
        """
        Save a scraped URL to file.
        
        Args:
            url: URL to save
        """
        try:
            with open(config.SCRAPED_URLS_FILE, 'a') as f:
                f.write(f"{url}\n")
            self.scraped_urls.add(url)
        except Exception as e:
            logger.error(f"Error saving scraped URL: {e}")
    
    def _setup_driver(self):
        """
        Set up Chrome WebDriver with appropriate options.
        """
        logger.info("Setting up Chrome WebDriver...")
        
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument('--headless')
            logger.info("Running in headless mode")
        
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Add user agent to appear more human-like
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.set_page_load_timeout(config.BROWSER_TIMEOUT)
            logger.info("Chrome WebDriver setup complete")
        except Exception as e:
            logger.error(f"Error setting up WebDriver: {e}")
            raise
    
    def login(self, username: str = None, password: str = None):
        """
        Log in to LinkedIn.
        
        Args:
            username: LinkedIn email/username (default from env)
            password: LinkedIn password (default from env)
        """
        if not self.driver:
            self._setup_driver()
        
        username = username or os.getenv('LINKEDIN_USERNAME')
        password = password or os.getenv('LINKEDIN_PASSWORD')
        
        if not username or not password:
            raise ValueError("LinkedIn credentials not provided. Set LINKEDIN_USERNAME and LINKEDIN_PASSWORD environment variables.")
        
        logger.info("Logging in to LinkedIn...")
        
        try:
            self.driver.get(config.LINKEDIN_LOGIN_URL)
            time.sleep(random.uniform(2, 4))
            
            # Find and fill username
            username_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            username_field.send_keys(username)
            time.sleep(random.uniform(0.5, 1.5))
            
            # Find and fill password
            password_field = self.driver.find_element(By.ID, "password")
            password_field.send_keys(password)
            time.sleep(random.uniform(0.5, 1.5))
            
            # Click login button
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            
            # Wait for login to complete
            time.sleep(5)
            
            # Check if login was successful
            if "feed" in self.driver.current_url or "checkpoint" in self.driver.current_url:
                logger.info("Login successful")
            else:
                logger.warning("Login may have failed - unexpected URL")
            
        except Exception as e:
            logger.error(f"Error during login: {e}")
            raise
    
    def _random_delay(self):
        """
        Apply a random delay between profile scrapes.
        """
        delay = random.randint(config.MIN_DELAY, config.MAX_DELAY)
        logger.info(f"Waiting {delay} seconds before next profile...")
        time.sleep(delay)
    
    def _get_profile_links(self, search_url: str, max_links: int = 50) -> List[str]:
        """
        Extract profile links from search results or feed.
        
        Args:
            search_url: LinkedIn search or feed URL
            max_links: Maximum number of links to extract
            
        Returns:
            List of profile URLs
        """
        logger.info(f"Navigating to: {search_url}")
        
        try:
            self.driver.get(search_url)
            time.sleep(random.uniform(3, 5))
            
            profile_links = set()
            scroll_attempts = 0
            max_scroll_attempts = 10
            
            while len(profile_links) < max_links and scroll_attempts < max_scroll_attempts:
                # Find all profile links
                links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/in/']")
                
                for link in links:
                    try:
                        href = link.get_attribute('href')
                        if href and '/in/' in href:
                            # Clean URL (remove query parameters)
                            clean_url = href.split('?')[0].rstrip('/')
                            if clean_url not in self.scraped_urls:
                                profile_links.add(clean_url)
                    except Exception:
                        pass
                
                # Scroll down to load more results
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(random.uniform(2, 4))
                scroll_attempts += 1
            
            logger.info(f"Found {len(profile_links)} profile links")
            return list(profile_links)[:max_links]
            
        except Exception as e:
            logger.error(f"Error extracting profile links: {e}")
            return []
    
    def _save_profile_data(self, profile_data: Dict[str, Any]):
        """
        Save profile data to JSON and CSV files.
        
        Args:
            profile_data: Profile data dictionary
        """
        try:
            # Save to JSON (append mode)
            json_data = []
            if os.path.exists(config.PROFILES_JSON):
                with open(config.PROFILES_JSON, 'r') as f:
                    try:
                        json_data = json.load(f)
                    except json.JSONDecodeError:
                        json_data = []
            
            json_data.append(profile_data)
            
            with open(config.PROFILES_JSON, 'w') as f:
                json.dump(json_data, f, indent=2)
            
            # Save to CSV (append mode)
            # Flatten nested structures for CSV
            flat_data = {
                'profile_url': profile_data.get('profile_url', ''),
                'scraped_at': profile_data.get('scraped_at', ''),
                'name': profile_data.get('name', ''),
                'headline': profile_data.get('headline', ''),
                'location': profile_data.get('location', ''),
                'about': profile_data.get('about', ''),
                'num_experiences': len(profile_data.get('experience', [])),
                'num_education': len(profile_data.get('education', [])),
                'num_skills': len(profile_data.get('skills', [])),
                'num_certifications': len(profile_data.get('certifications', [])),
                'num_languages': len(profile_data.get('languages', []))
            }
            
            file_exists = os.path.exists(config.PROFILES_CSV)
            
            with open(config.PROFILES_CSV, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=flat_data.keys())
                
                if not file_exists:
                    writer.writeheader()
                
                writer.writerow(flat_data)
            
            logger.info(f"Profile data saved for: {profile_data.get('name', 'Unknown')}")
            
        except Exception as e:
            logger.error(f"Error saving profile data: {e}")
    
    def scrape_profile(self, profile_url: str) -> Optional[Dict[str, Any]]:
        """
        Scrape a single LinkedIn profile.
        
        Args:
            profile_url: URL of the profile to scrape
            
        Returns:
            Profile data dictionary or None if failed
        """
        if profile_url in self.scraped_urls:
            logger.info(f"Profile already scraped: {profile_url}")
            return None
        
        try:
            logger.info(f"Navigating to profile: {profile_url}")
            self.driver.get(profile_url)
            time.sleep(random.uniform(3, 5))
            
            # Extract profile data
            profile_data = extract_profile_data(self.driver, profile_url)
            
            # Save data
            self._save_profile_data(profile_data)
            self._save_scraped_url(profile_url)
            
            return profile_data
            
        except Exception as e:
            logger.error(f"Error scraping profile {profile_url}: {e}")
            return None
    
    def scrape_profiles(self, search_url: str = None, max_profiles: int = 50):
        """
        Scrape multiple LinkedIn profiles from search results.
        
        Args:
            search_url: LinkedIn search URL (default: feed)
            max_profiles: Maximum number of profiles to scrape
        """
        if not self.driver:
            raise RuntimeError("Driver not initialized. Call login() first.")
        
        search_url = search_url or config.LINKEDIN_FEED_URL
        
        logger.info(f"Starting profile scraping session (max {max_profiles} profiles)")
        logger.info(f"Search URL: {search_url}")
        
        # Check if we're within operating hours
        if not should_continue_scraping():
            logger.warning("Cannot start scraping - outside operating hours")
            return
        
        # Get profile links
        profile_links = self._get_profile_links(search_url, max_profiles)
        
        if not profile_links:
            logger.warning("No profile links found")
            return
        
        # Scrape each profile
        scraped_count = 0
        
        for i, profile_url in enumerate(profile_links):
            # Check time before each profile
            if not should_continue_scraping():
                logger.warning(f"Stopping after {scraped_count} profiles due to time constraints")
                break
            
            logger.info(f"Processing profile {i+1}/{len(profile_links)}")
            
            profile_data = self.scrape_profile(profile_url)
            
            if profile_data:
                scraped_count += 1
                logger.info(f"Successfully scraped {scraped_count}/{max_profiles} profiles")
            
            # Apply random delay before next profile (unless it's the last one)
            if i < len(profile_links) - 1 and scraped_count < max_profiles:
                self._random_delay()
            
            # Stop if we've reached the max
            if scraped_count >= max_profiles:
                logger.info(f"Reached maximum of {max_profiles} profiles")
                break
        
        logger.info(f"Scraping session complete. Total profiles scraped: {scraped_count}")
    
    def close(self):
        """
        Close the browser and clean up resources.
        """
        if self.driver:
            logger.info("Closing browser...")
            self.driver.quit()
            self.driver = None
            logger.info("Browser closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


def main():
    """
    Example usage of the LinkedIn scraper.
    """
    # Example search URL (customize as needed)
    search_url = "https://www.linkedin.com/search/results/people/?keywords=software+engineer&origin=SWITCH_SEARCH_VERTICAL"
    
    with LinkedInScraper() as scraper:
        scraper.login()
        scraper.scrape_profiles(search_url=search_url, max_profiles=10)


if __name__ == "__main__":
    main()
