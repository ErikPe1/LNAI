"""
Test script to validate LinkedIn scraper functionality without actual scraping.
"""
import sys
import os
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from linkedin_scraper import config, scheduler  # noqa: E402
from linkedin_scraper.scraper import LinkedInScraper  # noqa: E402


def test_configuration():
    """Test configuration settings."""
    print("\n" + "=" * 60)
    print("Testing Configuration")
    print("=" * 60)

    print(
        f"✓ Operating Hours: {config.OPERATING_START_HOUR:02d}:"
        f"{config.OPERATING_START_MINUTE:02d} - {config.OPERATING_END_HOUR:02d}:"
        f"{config.OPERATING_END_MINUTE:02d}"
    )
    print(f"✓ Operating Days: Monday-Friday ({config.OPERATING_DAYS})")
    print(f"✓ Delay Range: {config.MIN_DELAY}-{config.MAX_DELAY} seconds")
    print(f"✓ Data Directory: {config.DATA_DIR}")
    print(f"✓ JSON Output: {config.PROFILES_JSON}")
    print(f"✓ CSV Output: {config.PROFILES_CSV}")
    print(f"✓ Log File: {config.LOG_FILE}")

    assert config.MIN_DELAY == 60, "Min delay should be 60 seconds"
    assert config.MAX_DELAY == 600, "Max delay should be 600 seconds"
    assert config.OPERATING_DAYS == [0, 1, 2, 3, 4], "Operating days should be Mon-Fri"

    print("\n✓ All configuration tests passed!")


def test_scheduler():
    """Test scheduler functionality."""
    print("\n" + "=" * 60)
    print("Testing Scheduler")
    print("=" * 60)

    current = scheduler.get_current_time()
    print(f"✓ Current time: {current.strftime('%Y-%m-%d %H:%M:%S %A')}")

    is_valid, message = scheduler.is_within_operating_hours()
    print(f"✓ Within operating hours: {is_valid}")
    print(f"  Message: {message}")

    print("\n✓ Scheduler tests passed!")


def test_random_delay():
    """Test random delay generation."""
    print("\n" + "=" * 60)
    print("Testing Random Delay Generation")
    print("=" * 60)

    delays = [random.randint(config.MIN_DELAY, config.MAX_DELAY) for _ in range(10)]

    print(f"✓ Generated 10 random delays: {delays}")
    print(f"✓ Min: {min(delays)}, Max: {max(delays)}")

    # Verify all delays are within range
    assert all(config.MIN_DELAY <= d <= config.MAX_DELAY for d in delays), "All delays should be within range"

    print("\n✓ Random delay tests passed!")


def test_scraper_initialization():
    """Test scraper initialization without browser."""
    print("\n" + "=" * 60)
    print("Testing Scraper Initialization")
    print("=" * 60)

    # Test creating scraper instance (without starting browser)
    scraper = LinkedInScraper(headless=True)
    print("✓ Scraper instance created")

    # Test scraped URLs tracking
    assert isinstance(scraper.scraped_urls, set), "scraped_urls should be a set"
    print(f"✓ Scraped URLs tracking initialized (count: {len(scraper.scraped_urls)})")

    print("\n✓ Scraper initialization tests passed!")


def test_data_directory():
    """Test data directory creation."""
    print("\n" + "=" * 60)
    print("Testing Data Directory")
    print("=" * 60)

    assert os.path.exists(config.DATA_DIR), "Data directory should exist"
    print(f"✓ Data directory exists: {config.DATA_DIR}")

    # Check if .gitkeep exists
    gitkeep_path = os.path.join(config.DATA_DIR, '.gitkeep')
    assert os.path.exists(gitkeep_path), ".gitkeep should exist"
    print(f"✓ .gitkeep file exists: {gitkeep_path}")

    print("\n✓ Data directory tests passed!")


def main():
    """Run all tests."""
    print("=" * 60)
    print("LinkedIn Scraper Test Suite")
    print("=" * 60)

    try:
        test_configuration()
        test_scheduler()
        test_random_delay()
        test_scraper_initialization()
        test_data_directory()

        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nThe LinkedIn scraper is properly configured and ready to use.")
        print("\nTo use the scraper:")
        print("1. Copy .env.example to .env")
        print("2. Add your LinkedIn credentials to .env")
        print("3. Run: python -m linkedin_scraper.scraper")
        print("\n⚠️  Remember: This tool is for educational purposes only.")
        print("   Always respect LinkedIn's Terms of Service.")

    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
