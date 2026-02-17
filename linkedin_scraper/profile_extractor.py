"""
Profile data extraction functions for LinkedIn profiles.
Extracts comprehensive information from profile pages.
"""
import logging
import time
import random
from typing import Dict, List, Any
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from . import config

logger = logging.getLogger(__name__)


def scroll_page(driver, delay: float = None):
    """
    Scroll through the entire page to load all dynamic content.

    Args:
        driver: Selenium WebDriver instance
        delay: Delay between scrolls (random if None)
    """
    if delay is None:
        delay = random.uniform(config.SCROLL_DELAY_MIN, config.SCROLL_DELAY_MAX)

    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(delay)

        # Calculate new scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")

        # Break if no new content loaded
        if new_height == last_height:
            # Try one more scroll to make sure
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(delay)
            final_height = driver.execute_script("return document.body.scrollHeight")
            if final_height == new_height:
                break

        last_height = new_height

    # Scroll back to top
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(delay)
    logger.debug("Page scroll completed")


def safe_get_text(element) -> str:
    """
    Safely extract text from an element.

    Args:
        element: Selenium WebElement

    Returns:
        Text content or empty string
    """
    try:
        return element.text.strip() if element else ""
    except Exception:
        return ""


def safe_find_element(driver, by, value, timeout=5):
    """
    Safely find an element with timeout.

    Args:
        driver: Selenium WebDriver instance
        by: Locator strategy
        value: Locator value
        timeout: Wait timeout

    Returns:
        Element or None
    """
    try:
        wait = WebDriverWait(driver, timeout)
        return wait.until(EC.presence_of_element_located((by, value)))
    except TimeoutException:
        return None


def safe_find_elements(driver, by, value, timeout=5):
    """
    Safely find multiple elements with timeout.

    Args:
        driver: Selenium WebDriver instance
        by: Locator strategy
        value: Locator value
        timeout: Wait timeout

    Returns:
        List of elements (empty if not found)
    """
    try:
        wait = WebDriverWait(driver, timeout)
        wait.until(EC.presence_of_element_located((by, value)))
        return driver.find_elements(by, value)
    except TimeoutException:
        return []


def extract_basic_info(driver) -> Dict[str, Any]:
    """
    Extract basic profile information (name, headline, location).

    Args:
        driver: Selenium WebDriver instance

    Returns:
        Dictionary with basic profile info
    """
    info = {}

    try:
        # Name
        name_element = safe_find_element(driver, By.CSS_SELECTOR, "h1.text-heading-xlarge")
        if not name_element:
            name_element = safe_find_element(driver, By.CSS_SELECTOR, "h1")
        info['name'] = safe_get_text(name_element)

        # Headline/Title
        headline_element = safe_find_element(driver, By.CSS_SELECTOR, "div.text-body-medium")
        info['headline'] = safe_get_text(headline_element)

        # Location
        location_element = safe_find_element(driver, By.CSS_SELECTOR, "span.text-body-small")
        info['location'] = safe_get_text(location_element)

        logger.debug(f"Extracted basic info: {info.get('name', 'Unknown')}")
    except Exception as e:
        logger.error(f"Error extracting basic info: {e}")

    return info


def extract_about(driver) -> str:
    """
    Extract About/Summary section.

    Args:
        driver: Selenium WebDriver instance

    Returns:
        About text
    """
    try:
        # Click "see more" if present
        see_more_buttons = safe_find_elements(driver, By.CSS_SELECTOR, "button[aria-label*='more']")
        for button in see_more_buttons:
            try:
                if button.is_displayed():
                    button.click()
                    time.sleep(0.5)
            except Exception:
                pass

        about_section = safe_find_element(driver, By.ID, "about")
        if about_section:
            parent = about_section.find_element(By.XPATH, "..")
            about_text = safe_get_text(parent)
            logger.debug("Extracted about section")
            return about_text
    except Exception as e:
        logger.error(f"Error extracting about section: {e}")

    return ""


def extract_experience(driver) -> List[Dict[str, str]]:
    """
    Extract work experience.

    Args:
        driver: Selenium WebDriver instance

    Returns:
        List of experience entries
    """
    experiences = []

    try:
        exp_section = safe_find_element(driver, By.ID, "experience")
        if exp_section:
            parent = exp_section.find_element(By.XPATH, "../..")
            exp_items = parent.find_elements(By.CSS_SELECTOR, "li.artdeco-list__item")

            for item in exp_items:
                exp_data = {}

                # Title
                title_elem = item.find_elements(By.CSS_SELECTOR, "span[aria-hidden='true']")
                if title_elem:
                    exp_data['title'] = safe_get_text(title_elem[0])

                # Company
                company_elems = item.find_elements(By.CSS_SELECTOR, "span.t-14")
                if len(company_elems) > 0:
                    exp_data['company'] = safe_get_text(company_elems[0])

                # Dates
                date_elems = item.find_elements(By.CSS_SELECTOR, "span.t-black--light")
                if date_elems:
                    exp_data['dates'] = safe_get_text(date_elems[0])

                # Location
                if len(company_elems) > 1:
                    exp_data['location'] = safe_get_text(company_elems[1])

                # Description
                desc_elem = item.find_elements(By.CSS_SELECTOR, "div.inline-show-more-text")
                if desc_elem:
                    exp_data['description'] = safe_get_text(desc_elem[0])

                if exp_data:
                    experiences.append(exp_data)

            logger.debug(f"Extracted {len(experiences)} experience entries")
    except Exception as e:
        logger.error(f"Error extracting experience: {e}")

    return experiences


def extract_education(driver) -> List[Dict[str, str]]:
    """
    Extract education information.

    Args:
        driver: Selenium WebDriver instance

    Returns:
        List of education entries
    """
    education = []

    try:
        edu_section = safe_find_element(driver, By.ID, "education")
        if edu_section:
            parent = edu_section.find_element(By.XPATH, "../..")
            edu_items = parent.find_elements(By.CSS_SELECTOR, "li.artdeco-list__item")

            for item in edu_items:
                edu_data = {}

                # School name
                school_elem = item.find_elements(By.CSS_SELECTOR, "span[aria-hidden='true']")
                if school_elem:
                    edu_data['school'] = safe_get_text(school_elem[0])

                # Degree info
                degree_elems = item.find_elements(By.CSS_SELECTOR, "span.t-14")
                if degree_elems:
                    edu_data['degree'] = safe_get_text(degree_elems[0])

                # Dates
                date_elems = item.find_elements(By.CSS_SELECTOR, "span.t-black--light")
                if date_elems:
                    edu_data['dates'] = safe_get_text(date_elems[0])

                if edu_data:
                    education.append(edu_data)

            logger.debug(f"Extracted {len(education)} education entries")
    except Exception as e:
        logger.error(f"Error extracting education: {e}")

    return education


def extract_skills(driver) -> List[str]:
    """
    Extract skills.

    Args:
        driver: Selenium WebDriver instance

    Returns:
        List of skills
    """
    skills = []

    try:
        # Try to click "Show all skills" button
        show_all_buttons = safe_find_elements(
            driver, By.XPATH,
            "//button[contains(., 'Show all') and contains(., 'skills')]"
        )
        for button in show_all_buttons:
            try:
                if button.is_displayed():
                    button.click()
                    time.sleep(1)
                    break
            except Exception:
                pass

        skills_section = safe_find_element(driver, By.ID, "skills")
        if skills_section:
            parent = skills_section.find_element(By.XPATH, "../..")
            skill_items = parent.find_elements(By.CSS_SELECTOR, "span[aria-hidden='true']")

            for item in skill_items:
                skill_text = safe_get_text(item)
                if skill_text and skill_text not in skills:
                    skills.append(skill_text)

            logger.debug(f"Extracted {len(skills)} skills")
    except Exception as e:
        logger.error(f"Error extracting skills: {e}")

    return skills


def extract_certifications(driver) -> List[Dict[str, str]]:
    """
    Extract certifications.

    Args:
        driver: Selenium WebDriver instance

    Returns:
        List of certification entries
    """
    certifications = []

    try:
        cert_section = safe_find_element(driver, By.XPATH, "//section[contains(@id, 'licenses_and_certifications')]")
        if cert_section:
            cert_items = cert_section.find_elements(By.CSS_SELECTOR, "li.artdeco-list__item")

            for item in cert_items:
                cert_data = {}

                # Certification name
                name_elem = item.find_elements(By.CSS_SELECTOR, "span[aria-hidden='true']")
                if name_elem:
                    cert_data['name'] = safe_get_text(name_elem[0])

                # Issuer
                issuer_elems = item.find_elements(By.CSS_SELECTOR, "span.t-14")
                if issuer_elems:
                    cert_data['issuer'] = safe_get_text(issuer_elems[0])

                # Date
                date_elems = item.find_elements(By.CSS_SELECTOR, "span.t-black--light")
                if date_elems:
                    cert_data['date'] = safe_get_text(date_elems[0])

                if cert_data:
                    certifications.append(cert_data)

            logger.debug(f"Extracted {len(certifications)} certifications")
    except Exception as e:
        logger.error(f"Error extracting certifications: {e}")

    return certifications


def extract_languages(driver) -> List[str]:
    """
    Extract languages.

    Args:
        driver: Selenium WebDriver instance

    Returns:
        List of languages
    """
    languages = []

    try:
        lang_section = safe_find_element(driver, By.XPATH, "//section[contains(@id, 'languages')]")
        if lang_section:
            lang_items = lang_section.find_elements(By.CSS_SELECTOR, "span[aria-hidden='true']")

            for item in lang_items:
                lang_text = safe_get_text(item)
                if lang_text and lang_text not in languages:
                    languages.append(lang_text)

            logger.debug(f"Extracted {len(languages)} languages")
    except Exception as e:
        logger.error(f"Error extracting languages: {e}")

    return languages


def extract_profile_data(driver, profile_url: str) -> Dict[str, Any]:
    """
    Extract all available data from a LinkedIn profile.

    Args:
        driver: Selenium WebDriver instance
        profile_url: URL of the profile being scraped

    Returns:
        Dictionary containing all extracted profile data
    """
    logger.info(f"Extracting data from profile: {profile_url}")

    # Scroll through the page to load all content
    scroll_page(driver)

    # Extract all sections
    profile_data = {
        'profile_url': profile_url,
        'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
    }

    # Basic info
    profile_data.update(extract_basic_info(driver))

    # About section
    profile_data['about'] = extract_about(driver)

    # Experience
    profile_data['experience'] = extract_experience(driver)

    # Education
    profile_data['education'] = extract_education(driver)

    # Skills
    profile_data['skills'] = extract_skills(driver)

    # Certifications
    profile_data['certifications'] = extract_certifications(driver)

    # Languages
    profile_data['languages'] = extract_languages(driver)

    logger.info(f"Successfully extracted data for: {profile_data.get('name', 'Unknown')}")

    return profile_data
