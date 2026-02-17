"""
Time-based scheduling logic for LinkedIn Profile Scraper
"""

import logging
from datetime import datetime
from typing import Tuple

from . import config

logger = logging.getLogger(__name__)


def is_within_operating_hours() -> bool:
    """
    Check if current time is within operating hours (Mon-Fri, 9am-4:30pm).
    
    Returns:
        bool: True if within operating hours, False otherwise
    """
    now = datetime.now(config.TIMEZONE)
    
    # Check if it's an operating day
    if now.weekday() not in config.OPERATING_DAYS:
        logger.info(
            f"Outside operating days. Current day: {now.strftime('%A')} "
            f"(Operating days: Monday-Friday)"
        )
        return False
    
    # Check if it's within operating hours
    start_time = now.replace(
        hour=config.OPERATING_HOURS["start_hour"],
        minute=config.OPERATING_HOURS["start_minute"],
        second=0,
        microsecond=0
    )
    end_time = now.replace(
        hour=config.OPERATING_HOURS["end_hour"],
        minute=config.OPERATING_HOURS["end_minute"],
        second=0,
        microsecond=0
    )
    
    if not (start_time <= now <= end_time):
        logger.info(
            f"Outside operating hours. Current time: {now.strftime('%I:%M %p')} "
            f"(Operating hours: {start_time.strftime('%I:%M %p')} - "
            f"{end_time.strftime('%I:%M %p')})"
        )
        return False
    
    return True


def get_current_time_info() -> Tuple[datetime, str]:
    """
    Get current time in configured timezone with formatted string.
    
    Returns:
        Tuple[datetime, str]: Current datetime and formatted string
    """
    now = datetime.now(config.TIMEZONE)
    formatted = now.strftime("%Y-%m-%d %I:%M:%S %p %Z")
    return now, formatted


def log_time_constraint_stop():
    """Log when scraper stops due to time constraints."""
    now, formatted = get_current_time_info()
    logger.warning(
        f"Scraper stopped due to time constraints. Current time: {formatted}"
    )
    logger.info(
        f"Operating hours: Monday-Friday, "
        f"{config.OPERATING_HOURS['start_hour']:02d}:"
        f"{config.OPERATING_HOURS['start_minute']:02d} - "
        f"{config.OPERATING_HOURS['end_hour']:02d}:"
        f"{config.OPERATING_HOURS['end_minute']:02d}"
    )
