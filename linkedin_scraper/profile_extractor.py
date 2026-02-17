"""
Profile data extraction functions for LinkedIn profiles
"""

import logging
import time
from typing import Dict, List, Any, Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logger = logging.getLogger(__name__)


def scroll_page_slowly(driver, scroll_pause_time: float = 2.0) -> None:
    """
    Scroll through the entire page slowly to load all dynamic content.
    
    Args:
        driver: Selenium WebDriver instance
        scroll_pause_time: Time to pause between scrolls
    """
    logger.debug("Scrolling through profile page to load all content")
    
    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        # Wait to load page
        time.sleep(scroll_pause_time)
        
        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    
    # Scroll back to top
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(1)


def safe_get_text(element) -> str:
    """
    Safely extract text from an element.
    
    Args:
        element: Selenium WebElement
        
    Returns:
        str: Text content or empty string if not available
    """
    try:
        return element.text.strip() if element else ""
    except Exception as e:
        logger.debug(f"Error extracting text: {e}")
        return ""


def extract_basic_info(driver) -> Dict[str, str]:
    """
    Extract basic profile information (name, headline, location).
    
    Args:
        driver: Selenium WebDriver instance
        
    Returns:
        Dict: Basic profile information
    """
    info = {
        "name": "",
        "headline": "",
        "location": "",
        "profile_url": driver.current_url
    }
    
    try:
        # Extract name
        name_element = driver.find_element(By.CSS_SELECTOR, "h1.text-heading-xlarge")
        info["name"] = safe_get_text(name_element)
        logger.debug(f"Extracted name: {info['name']}")
    except NoSuchElementException:
        logger.warning("Could not find name element")
    
    try:
        # Extract headline
        headline_element = driver.find_element(By.CSS_SELECTOR, "div.text-body-medium")
        info["headline"] = safe_get_text(headline_element)
        logger.debug(f"Extracted headline: {info['headline']}")
    except NoSuchElementException:
        logger.warning("Could not find headline element")
    
    try:
        # Extract location
        location_element = driver.find_element(By.CSS_SELECTOR, "span.text-body-small")
        info["location"] = safe_get_text(location_element)
        logger.debug(f"Extracted location: {info['location']}")
    except NoSuchElementException:
        logger.warning("Could not find location element")
    
    return info


def extract_about_section(driver) -> str:
    """
    Extract the About/Summary section.
    
    Args:
        driver: Selenium WebDriver instance
        
    Returns:
        str: About section text
    """
    try:
        # Try to expand "see more" if present
        try:
            see_more = driver.find_element(
                By.CSS_SELECTOR, 
                "button[aria-label*='more about']"
            )
            see_more.click()
            time.sleep(1)
        except NoSuchElementException:
            pass
        
        about_element = driver.find_element(
            By.CSS_SELECTOR,
            "section[data-section='summary'] div.display-flex.ph5.pv3"
        )
        about_text = safe_get_text(about_element)
        logger.debug(f"Extracted about section: {len(about_text)} characters")
        return about_text
    except NoSuchElementException:
        logger.debug("No about section found")
        return ""


def extract_experience(driver) -> List[Dict[str, str]]:
    """
    Extract experience/work history.
    
    Args:
        driver: Selenium WebDriver instance
        
    Returns:
        List[Dict]: List of experience entries
    """
    experiences = []
    
    try:
        # Try to expand all experiences
        try:
            show_all_button = driver.find_element(
                By.CSS_SELECTOR,
                "section[data-section='experience'] button[aria-label*='Show all']"
            )
            show_all_button.click()
            time.sleep(2)
        except NoSuchElementException:
            pass
        
        experience_items = driver.find_elements(
            By.CSS_SELECTOR,
            "section[data-section='experience'] li.artdeco-list__item"
        )
        
        for item in experience_items:
            exp = {}
            try:
                exp["title"] = safe_get_text(
                    item.find_element(By.CSS_SELECTOR, "div.display-flex span[aria-hidden='true']")
                )
                exp["company"] = safe_get_text(
                    item.find_element(By.CSS_SELECTOR, "span.t-14.t-normal span[aria-hidden='true']")
                )
                exp["dates"] = safe_get_text(
                    item.find_element(By.CSS_SELECTOR, "span.t-14.t-normal.t-black--light span[aria-hidden='true']")
                )
                exp["description"] = safe_get_text(
                    item.find_element(By.CSS_SELECTOR, "div.display-flex span[aria-hidden='true']")
                )
                experiences.append(exp)
            except NoSuchElementException:
                continue
        
        logger.debug(f"Extracted {len(experiences)} experience entries")
    except NoSuchElementException:
        logger.debug("No experience section found")
    
    return experiences


def extract_education(driver) -> List[Dict[str, str]]:
    """
    Extract education information.
    
    Args:
        driver: Selenium WebDriver instance
        
    Returns:
        List[Dict]: List of education entries
    """
    education_list = []
    
    try:
        education_items = driver.find_elements(
            By.CSS_SELECTOR,
            "section[data-section='education'] li.artdeco-list__item"
        )
        
        for item in education_items:
            edu = {}
            try:
                edu["school"] = safe_get_text(
                    item.find_element(By.CSS_SELECTOR, "div.display-flex span[aria-hidden='true']")
                )
                edu["degree"] = safe_get_text(
                    item.find_element(By.CSS_SELECTOR, "span.t-14.t-normal span[aria-hidden='true']")
                )
                edu["dates"] = safe_get_text(
                    item.find_element(By.CSS_SELECTOR, "span.t-14.t-normal.t-black--light span[aria-hidden='true']")
                )
                education_list.append(edu)
            except NoSuchElementException:
                continue
        
        logger.debug(f"Extracted {len(education_list)} education entries")
    except NoSuchElementException:
        logger.debug("No education section found")
    
    return education_list


def extract_skills(driver) -> List[str]:
    """
    Extract skills list.
    
    Args:
        driver: Selenium WebDriver instance
        
    Returns:
        List[str]: List of skills
    """
    skills = []
    
    try:
        # Try to show all skills
        try:
            show_all_button = driver.find_element(
                By.CSS_SELECTOR,
                "section[data-section='skills'] button[aria-label*='Show all']"
            )
            show_all_button.click()
            time.sleep(2)
        except NoSuchElementException:
            pass
        
        skill_elements = driver.find_elements(
            By.CSS_SELECTOR,
            "section[data-section='skills'] span[aria-hidden='true']"
        )
        
        for element in skill_elements:
            skill = safe_get_text(element)
            if skill and skill not in skills:
                skills.append(skill)
        
        logger.debug(f"Extracted {len(skills)} skills")
    except NoSuchElementException:
        logger.debug("No skills section found")
    
    return skills


def extract_profile_data(driver) -> Dict[str, Any]:
    """
    Extract all available data from a LinkedIn profile.
    
    Args:
        driver: Selenium WebDriver instance
        
    Returns:
        Dict: Complete profile data
    """
    logger.info(f"Extracting profile data from: {driver.current_url}")
    
    # Scroll through page to load all content
    scroll_page_slowly(driver)
    
    # Extract all profile sections
    profile_data = {
        "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        **extract_basic_info(driver),
        "about": extract_about_section(driver),
        "experience": extract_experience(driver),
        "education": extract_education(driver),
        "skills": extract_skills(driver),
    }
    
    logger.info(f"Successfully extracted profile data for: {profile_data.get('name', 'Unknown')}")
    return profile_data
