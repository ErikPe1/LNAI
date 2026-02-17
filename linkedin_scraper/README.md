# LinkedIn Profile Scraper

An automated LinkedIn profile scraper with intelligent scheduling, random delays, and comprehensive data extraction.

## ⚠️ IMPORTANT LEGAL DISCLAIMER

**THIS TOOL IS FOR EDUCATIONAL PURPOSES ONLY**

- **LinkedIn Terms of Service**: This scraper may violate LinkedIn's Terms of Service. Using automated tools to scrape LinkedIn is against their ToS and may result in account suspension or legal action.
- **Official API**: LinkedIn provides an official API for legitimate use cases. Please use the [LinkedIn API](https://www.linkedin.com/developers/) instead.
- **Ethical Use**: Always respect website terms of service, robots.txt, and data privacy laws (GDPR, CCPA, etc.).
- **Personal Responsibility**: You are solely responsible for how you use this tool. The authors are not liable for any consequences.
- **Rate Limiting**: LinkedIn actively monitors and blocks suspicious activity. Use at your own risk.

**We strongly recommend using LinkedIn's official API for any production use case.**

## Features

- ✅ Automated profile navigation and data extraction
- ✅ Time-based scheduling (Monday-Friday, 9:00 AM - 4:30 PM)
- ✅ Random delays (60-600 seconds) between profiles
- ✅ Comprehensive data extraction (name, headline, experience, education, skills, etc.)
- ✅ JSON and CSV data storage
- ✅ Duplicate prevention
- ✅ Robust error handling
- ✅ Detailed logging
- ✅ Graceful shutdown on time constraints

## Installation

### Prerequisites

- Python 3.9 or higher
- Chrome browser installed
- LinkedIn account

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/ErikPe1/LNAI.git
   cd LNAI/linkedin_scraper
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your LinkedIn credentials
   ```

4. **Set your LinkedIn credentials in `.env`**
   ```bash
   LINKEDIN_USERNAME=your_email@example.com
   LINKEDIN_PASSWORD=your_password
   TIMEZONE=UTC
   HEADLESS_MODE=False
   LOG_LEVEL=INFO
   ```

## Usage

### Basic Usage

```python
from linkedin_scraper import LinkedInScraper

# Create scraper instance
with LinkedInScraper() as scraper:
    # Login to LinkedIn
    scraper.login()
    
    # Scrape profiles from search results
    scraper.scrape_profiles(
        search_url="https://www.linkedin.com/search/results/people/?keywords=software+engineer",
        max_profiles=10
    )
```

### Advanced Usage

```python
from linkedin_scraper import LinkedInScraper

# Run in headless mode
scraper = LinkedInScraper(headless=True)

try:
    # Login with explicit credentials
    scraper.login(
        username="your_email@example.com",
        password="your_password"
    )
    
    # Scrape from custom search
    scraper.scrape_profiles(
        search_url="https://www.linkedin.com/search/results/people/?keywords=data+scientist&location=San+Francisco",
        max_profiles=50
    )
finally:
    scraper.close()
```

### Command Line

```bash
# Run the scraper
python -m linkedin_scraper.scraper
```

## Configuration

Edit `config.py` to customize:

- **Operating Hours**: Default 9:00 AM - 4:30 PM
- **Operating Days**: Monday-Friday (0-4)
- **Delay Range**: 60-600 seconds
- **Timezone**: UTC (or set via environment variable)
- **Data Storage**: `data/profiles.json` and `data/profiles.csv`

## Data Extraction

The scraper extracts the following information from each profile:

### Basic Information
- Name
- Headline/Title
- Location
- Profile URL

### Detailed Sections
- **About**: Summary/bio section
- **Experience**: Job history with titles, companies, dates, locations, descriptions
- **Education**: Schools, degrees, dates
- **Skills**: List of skills
- **Certifications**: Certifications with issuer and date
- **Languages**: Spoken languages

### Data Format

**JSON Format** (`data/profiles.json`):
```json
[
  {
    "profile_url": "https://www.linkedin.com/in/john-doe",
    "scraped_at": "2024-01-15 10:30:00",
    "name": "John Doe",
    "headline": "Software Engineer at Tech Co",
    "location": "San Francisco, CA",
    "about": "Passionate software engineer...",
    "experience": [
      {
        "title": "Senior Software Engineer",
        "company": "Tech Co",
        "dates": "Jan 2020 - Present",
        "location": "San Francisco, CA",
        "description": "Leading backend development..."
      }
    ],
    "education": [...],
    "skills": ["Python", "JavaScript", "React"],
    "certifications": [...],
    "languages": ["English", "Spanish"]
  }
]
```

**CSV Format** (`data/profiles.csv`):
Contains summarized data with counts for nested sections.

## Scheduling

The scraper automatically respects time constraints:

- **Operating Hours**: 9:00 AM - 4:30 PM
- **Operating Days**: Monday - Friday
- **Time Checks**: Before starting and before each profile
- **Graceful Shutdown**: Stops immediately when outside hours

Configure timezone in `.env`:
```bash
TIMEZONE=America/New_York
```

## Delays

Random delays are applied to mimic human behavior:

- **Between Profiles**: 60-600 seconds (1-10 minutes)
- **Page Scrolling**: 1-3 seconds
- **Clicks**: 2-5 seconds

## Logging

Logs are saved to `data/scraper.log` and printed to console.

**Log Levels**: DEBUG, INFO, WARNING, ERROR

Example logs:
```
2024-01-15 10:30:00 - INFO - LinkedInScraper initialized
2024-01-15 10:30:05 - INFO - Login successful
2024-01-15 10:30:10 - INFO - Within operating hours. Current time: 10:30
2024-01-15 10:30:15 - INFO - Extracting data from profile: https://linkedin.com/in/john-doe
2024-01-15 10:30:30 - INFO - Waiting 245 seconds before next profile...
```

## Error Handling

The scraper handles:

- **Network Errors**: Retries and continues to next profile
- **Missing Elements**: Gracefully skips unavailable data
- **Rate Limiting**: Logs warnings and continues
- **Login Issues**: Clear error messages
- **Time Constraints**: Automatic shutdown

## File Structure

```
linkedin_scraper/
├── __init__.py              # Package initialization
├── config.py                # Configuration constants
├── scheduler.py             # Time-based scheduling logic
├── profile_extractor.py     # Profile data extraction
├── scraper.py               # Main scraper class
├── requirements.txt         # Python dependencies
├── .env.example             # Example environment variables
├── README.md                # This file
└── data/
    ├── .gitkeep             # Keep directory in git
    ├── profiles.json        # Scraped data (JSON)
    ├── profiles.csv         # Scraped data (CSV)
    ├── scraped_urls.txt     # Tracking file
    └── scraper.log          # Log file
```

## Troubleshooting

### Login Fails

- Verify credentials in `.env`
- Check for LinkedIn CAPTCHA or email verification
- Try logging in manually first
- LinkedIn may block automated logins - use official API

### No Profiles Found

- Check search URL is valid
- Ensure you're logged in
- LinkedIn may have changed HTML structure
- Try different search queries

### Rate Limited

- Increase delay range in `config.py`
- Reduce `max_profiles`
- LinkedIn actively blocks bots - use responsibly

### ChromeDriver Issues

- Ensure Chrome browser is installed
- `webdriver-manager` should auto-download driver
- Update Chrome to latest version
- Try different ChromeDriver version

### Time Zone Issues

- Set correct timezone in `.env`
- Use standard timezone names (e.g., `America/New_York`, `Europe/London`)
- Check system time is correct

## Development

### Running Tests

```bash
# Install dev dependencies
pip install pytest pytest-cov

# Run tests
pytest
```

### Code Style

```bash
# Install formatters
pip install black flake8

# Format code
black linkedin_scraper/

# Lint
flake8 linkedin_scraper/
```

## Alternatives

**Recommended alternatives to scraping:**

1. **LinkedIn Official API**: https://www.linkedin.com/developers/
2. **LinkedIn Sales Navigator**: Official LinkedIn tool for finding leads
3. **LinkedIn Recruiter**: Official recruiting platform
4. **Data Providers**: Companies that legally aggregate LinkedIn data

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is for educational purposes only. Use at your own risk.

## Support

For issues and questions:
- Open an issue on GitHub
- Check existing issues for solutions

## Changelog

### Version 1.0.0 (2024-01-15)
- Initial release
- Basic profile scraping
- Time-based scheduling
- Random delays
- JSON/CSV export
- Error handling and logging

---

**Remember**: Always respect website terms of service and use official APIs when available. This tool is for educational purposes only.
