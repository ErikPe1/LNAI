"""
Time-based scheduling logic for LinkedIn scraper.
Ensures scraper only runs during operating hours.
"""
import logging
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Tuple
from . import config

logger = logging.getLogger(__name__)


def get_current_time(timezone: str = None) -> datetime:
    """
    Get current time in the specified timezone.

    Args:
        timezone: Timezone string (e.g., 'UTC', 'America/New_York')

    Returns:
        Current datetime in specified timezone
    """
    tz = timezone or config.TIMEZONE
    try:
        return datetime.now(ZoneInfo(tz))
    except Exception as e:
        logger.warning(f"Invalid timezone '{tz}', falling back to UTC: {e}")
        return datetime.now(ZoneInfo('UTC'))


def is_within_operating_hours(current_time: datetime = None) -> Tuple[bool, str]:
    """
    Check if current time is within operating hours (Mon-Fri, 9am-4:30pm).

    Args:
        current_time: DateTime to check (defaults to now)

    Returns:
        Tuple of (is_valid, reason_message)
    """
    if current_time is None:
        current_time = get_current_time()

    # Check day of week (0=Monday, 6=Sunday)
    weekday = current_time.weekday()
    if weekday not in config.OPERATING_DAYS:
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        return False, f"Outside operating days. Today is {day_names[weekday]}, but scraper only runs Monday-Friday."

    # Check time of day
    current_hour = current_time.hour
    current_minute = current_time.minute

    # Convert to minutes for easier comparison
    current_minutes = current_hour * 60 + current_minute
    start_minutes = config.OPERATING_START_HOUR * 60 + config.OPERATING_START_MINUTE
    end_minutes = config.OPERATING_END_HOUR * 60 + config.OPERATING_END_MINUTE

    if current_minutes < start_minutes:
        return False, (
            f"Before operating hours. Current time: {current_time.strftime('%H:%M')}, "
            f"Operating hours: {config.OPERATING_START_HOUR:02d}:{config.OPERATING_START_MINUTE:02d}"
            f"-{config.OPERATING_END_HOUR:02d}:{config.OPERATING_END_MINUTE:02d}"
        )

    if current_minutes > end_minutes:
        return False, (
            f"After operating hours. Current time: {current_time.strftime('%H:%M')}, "
            f"Operating hours: {config.OPERATING_START_HOUR:02d}:{config.OPERATING_START_MINUTE:02d}"
            f"-{config.OPERATING_END_HOUR:02d}:{config.OPERATING_END_MINUTE:02d}"
        )

    return True, f"Within operating hours. Current time: {current_time.strftime('%H:%M')}"


def should_continue_scraping() -> bool:
    """
    Check if scraping should continue based on current time.
    Logs the decision.

    Returns:
        True if scraping should continue, False otherwise
    """
    is_valid, message = is_within_operating_hours()

    if is_valid:
        logger.info(message)
        return True
    else:
        logger.warning(f"Stopping scraper: {message}")
        return False
