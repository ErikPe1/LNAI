#!/usr/bin/env python3
"""
Example script to run the LinkedIn Profile Scraper
"""

import sys
import os
from dotenv import load_dotenv
from linkedin_scraper import LinkedInScraper


def main():
    """Main entry point for the scraper."""
    # Load environment variables
    load_dotenv()
    
    # Parse command line arguments
    if len(sys.argv) < 2:
        print("LinkedIn Profile Scraper")
        print("\nUsage:")
        print("  python run_scraper.py <search_url> [max_profiles]")
        print("\nExample:")
        print('  python run_scraper.py "https://linkedin.com/search/results/people/?keywords=software+engineer" 25')
        print("\nMake sure to set LINKEDIN_EMAIL and LINKEDIN_PASSWORD in .env file!")
        sys.exit(1)
    
    search_url = sys.argv[1]
    max_profiles = int(sys.argv[2]) if len(sys.argv) > 2 else 50
    
    print("=" * 70)
    print("LinkedIn Profile Scraper")
    print("=" * 70)
    print(f"Search URL: {search_url}")
    print(f"Max profiles: {max_profiles}")
    print("=" * 70)
    print("\n⚠️  WARNING: Using this tool may violate LinkedIn's Terms of Service!")
    print("Use at your own risk.\n")
    
    # Confirm to proceed
    response = input("Do you want to proceed? (yes/no): ")
    if response.lower() not in ["yes", "y"]:
        print("Aborted.")
        sys.exit(0)
    
    # Run scraper
    try:
        with LinkedInScraper() as scraper:
            print("\n🔐 Logging in to LinkedIn...")
            scraper.login()
            
            print("✅ Login successful!")
            print(f"\n🚀 Starting to scrape profiles...")
            print("=" * 70)
            
            scraper.scrape_profiles(search_url, max_profiles)
            
            print("\n" + "=" * 70)
            print("✨ Scraping completed successfully!")
            print(f"📊 Check data in: linkedin_scraper/data/")
            print(f"📝 Check logs in: linkedin_scraper.log")
            print("=" * 70)
    
    except ValueError as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure to:")
        print("1. Copy .env.example to .env")
        print("2. Set LINKEDIN_EMAIL and LINKEDIN_PASSWORD in .env")
        sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user. Cleaning up...")
        sys.exit(0)
    
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        print("Check linkedin_scraper.log for details")
        sys.exit(1)


if __name__ == "__main__":
    main()
