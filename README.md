# LNAI - LinkedIn AI Profile Scraper

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

Automated LinkedIn profile scraper with intelligent scheduling and comprehensive data extraction.

## ⚠️ Important Legal & Ethical Considerations

**WARNING**: This tool is for educational purposes only. 

### LinkedIn Terms of Service
- LinkedIn's Terms of Service **explicitly prohibit** scraping, crawling, or automated data collection
- Using this tool may result in account suspension or permanent ban
- LinkedIn actively detects and blocks automated tools

### Recommended Alternatives
- **LinkedIn API**: Use LinkedIn's official API for authorized data access
- **LinkedIn Sales Navigator**: Legitimate tool for lead generation
- **Manual Research**: Direct profile viewing within LinkedIn's platform

### Responsible Use
If you choose to use this tool:
- Only scrape publicly available information
- Respect robots.txt and rate limits
- Never scrape personal/private information
- Use data ethically and legally
- Comply with GDPR, CCPA, and other privacy laws
- Consider the privacy rights of individuals

**By using this tool, you accept full responsibility for any consequences.**

---

## Features

✨ **Comprehensive Data Extraction**
- Basic information (name, headline, location)
- About/Summary section
- Complete work experience history
- Education background
- Skills endorsements
- And more...

⏰ **Intelligent Scheduling**
- Operates only during business hours (Monday-Friday, 9 AM - 4:30 PM)
- Automatic time-based shutdown
- Timezone-aware scheduling

🤖 **Human-like Behavior**
- Random delays (60-600 seconds) between profiles
- Natural scrolling patterns
- Variable interaction timing
- Anti-detection measures

📊 **Flexible Data Storage**
- JSON format (complete structured data)
- CSV format (flattened summary)
- Automatic duplicate prevention

🛡️ **Robust Error Handling**
- Network error recovery
- Missing element handling
- Comprehensive logging
- Session management

---

## Installation

### Prerequisites
- Python 3.8 or higher
- Chrome browser installed
- LinkedIn account

### Setup Steps

1. **Clone the repository**
```bash
git clone https://github.com/ErikPe1/LNAI.git
cd LNAI
```

2. **Create virtual environment** (recommended)
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure credentials**
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your LinkedIn credentials
# NEVER commit .env to version control!
```

Edit `.env`:
```env
LINKEDIN_EMAIL=your_email@example.com
LINKEDIN_PASSWORD=your_secure_password
```

---

## Usage

### Basic Example

```python
from linkedin_scraper import LinkedInScraper

# Initialize scraper (credentials loaded from .env)
scraper = LinkedInScraper()

# Login to LinkedIn
scraper.login()

# Scrape profiles from search results
scraper.scrape_profiles(
    search_url="https://linkedin.com/search/results/people/?keywords=software+engineer",
    max_profiles=50
)

# Close browser when done
scraper.close()
```

### Context Manager (Recommended)

```python
from linkedin_scraper import LinkedInScraper

with LinkedInScraper() as scraper:
    scraper.login()
    scraper.scrape_profiles(
        search_url="https://linkedin.com/search/results/people/?keywords=data+scientist",
        max_profiles=25
    )
```

### Single Profile

```python
from linkedin_scraper import LinkedInScraper

with LinkedInScraper() as scraper:
    scraper.login()
    profile_data = scraper.scrape_profile(
        "https://www.linkedin.com/in/example-profile/"
    )
    print(profile_data)
```

### Command Line Usage

Create a script `run_scraper.py`:

```python
#!/usr/bin/env python3
from linkedin_scraper import LinkedInScraper
import sys

def main():
    search_url = sys.argv[1] if len(sys.argv) > 1 else None
    max_profiles = int(sys.argv[2]) if len(sys.argv) > 2 else 50
    
    if not search_url:
        print("Usage: python run_scraper.py <search_url> [max_profiles]")
        sys.exit(1)
    
    with LinkedInScraper() as scraper:
        scraper.login()
        scraper.scrape_profiles(search_url, max_profiles)

if __name__ == "__main__":
    main()
```

Run it:
```bash
python run_scraper.py "https://linkedin.com/search/results/people/?keywords=python+developer" 30
```

---

## Configuration

Edit `linkedin_scraper/config.py` to customize:

### Operating Hours
```python
OPERATING_HOURS = {
    "start_hour": 9,      # 9:00 AM
    "start_minute": 0,
    "end_hour": 16,       # 4:00 PM
    "end_minute": 30,     # 4:30 PM
}

OPERATING_DAYS = [0, 1, 2, 3, 4]  # Monday through Friday
```

### Delays
```python
MIN_DELAY = 60   # Minimum delay between profiles (seconds)
MAX_DELAY = 600  # Maximum delay between profiles (seconds)
```

### Time Zone
```python
import pytz
TIMEZONE = pytz.timezone("America/New_York")
```

### Browser Mode
```python
HEADLESS_MODE = False  # Set to True for headless operation
```

---

## Output Data

### Data Location
- **JSON**: `linkedin_scraper/data/linkedin_profiles.json`
- **CSV**: `linkedin_scraper/data/linkedin_profiles.csv`
- **Logs**: `linkedin_scraper.log`

### JSON Structure
```json
[
  {
    "scraped_at": "2024-01-15 10:30:45",
    "name": "John Doe",
    "headline": "Senior Software Engineer at Tech Corp",
    "location": "San Francisco, CA",
    "profile_url": "https://www.linkedin.com/in/johndoe/",
    "about": "Passionate software engineer with 10+ years...",
    "experience": [
      {
        "title": "Senior Software Engineer",
        "company": "Tech Corp",
        "dates": "Jan 2020 - Present",
        "description": "Leading development of..."
      }
    ],
    "education": [
      {
        "school": "Stanford University",
        "degree": "BS Computer Science",
        "dates": "2010 - 2014"
      }
    ],
    "skills": ["Python", "JavaScript", "Machine Learning"]
  }
]
```

### CSV Structure
| Column | Description |
|--------|-------------|
| scraped_at | Timestamp of scraping |
| name | Full name |
| headline | Professional headline |
| location | Geographic location |
| profile_url | LinkedIn profile URL |
| about | About section text |
| num_experiences | Number of experience entries |
| num_education | Number of education entries |
| num_skills | Number of skills |

---

## Architecture

### Project Structure
```
LNAI/
├── linkedin_scraper/
│   ├── __init__.py           # Package initialization
│   ├── scraper.py            # Main scraper class
│   ├── profile_extractor.py  # Data extraction logic
│   ├── scheduler.py          # Time-based scheduling
│   ├── config.py             # Configuration settings
│   └── data/                 # Output directory
│       ├── .gitkeep
│       ├── linkedin_profiles.json
│       └── linkedin_profiles.csv
├── requirements.txt          # Python dependencies
├── .env.example             # Environment template
├── .env                     # Your credentials (gitignored)
└── README.md               # This file
```

### Key Components

#### 1. LinkedInScraper (`scraper.py`)
Main scraper class handling:
- Browser automation
- Authentication
- Profile navigation
- Delay management
- Data storage

#### 2. Profile Extractor (`profile_extractor.py`)
Extraction functions for:
- Basic information
- About section
- Experience history
- Education
- Skills

#### 3. Scheduler (`scheduler.py`)
Time management:
- Operating hours check
- Time constraint logging
- Timezone handling

#### 4. Configuration (`config.py`)
Centralized settings:
- Operating schedule
- Delay parameters
- URLs and selectors
- Data paths

---

## Troubleshooting

### Common Issues

#### 1. Login Fails
**Problem**: Can't log in to LinkedIn

**Solutions**:
- Verify credentials in `.env` file
- Check for CAPTCHA (may require manual intervention)
- Try logging in manually first in the same browser
- LinkedIn may have flagged your account for suspicious activity

#### 2. Elements Not Found
**Problem**: Scraper can't find profile elements

**Solutions**:
- LinkedIn frequently changes their HTML structure
- Update CSS selectors in `profile_extractor.py`
- Check if you're logged in properly
- Verify profile is publicly accessible

#### 3. Account Blocked/Suspended
**Problem**: LinkedIn blocks your account

**Solutions**:
- This is expected behavior if detected
- Create a new account (use at your own risk)
- Use LinkedIn's official API instead
- Reduce scraping frequency

#### 4. ChromeDriver Issues
**Problem**: WebDriver errors

**Solutions**:
```bash
# Update Chrome to latest version
# Then reinstall webdriver-manager
pip install --upgrade webdriver-manager
```

#### 5. Time Zone Issues
**Problem**: Scraper runs at wrong times

**Solutions**:
```python
# In config.py, adjust timezone
import pytz
TIMEZONE = pytz.timezone("Your/Timezone")  # e.g., "Europe/London"
```

#### 6. Data Not Saving
**Problem**: Profiles scraped but no output files

**Solutions**:
- Check `linkedin_scraper/data/` directory exists
- Verify write permissions
- Check logs in `linkedin_scraper.log`

---

## Development

### Running Tests
```bash
# Install dev dependencies
pip install pytest pytest-cov

# Run tests (when implemented)
pytest tests/
```

### Code Style
```bash
# Install linting tools
pip install black flake8 mypy

# Format code
black linkedin_scraper/

# Lint
flake8 linkedin_scraper/

# Type check
mypy linkedin_scraper/
```

---

## Logging

The scraper creates detailed logs in `linkedin_scraper.log`:

```
2024-01-15 10:30:00 - linkedin_scraper.scraper - INFO - LinkedIn Scraper initialized
2024-01-15 10:30:05 - linkedin_scraper.scraper - INFO - Logging in to LinkedIn
2024-01-15 10:30:15 - linkedin_scraper.scraper - INFO - Successfully logged in to LinkedIn
2024-01-15 10:30:20 - linkedin_scraper.scraper - INFO - Scraping profile: https://...
2024-01-15 10:31:45 - linkedin_scraper.scraper - INFO - Successfully scraped profile: John Doe
2024-01-15 10:31:45 - linkedin_scraper.scraper - INFO - Waiting 347 seconds before next profile...
```

---

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## Disclaimer

This software is provided for **educational purposes only**. The authors and contributors:

- Do NOT endorse violating LinkedIn's Terms of Service
- Are NOT responsible for account suspensions or bans
- Are NOT liable for any legal consequences
- Do NOT guarantee the software will work or remain undetected
- Strongly recommend using LinkedIn's official API

**Use at your own risk. You have been warned.**

---

## Alternatives

Consider these legitimate alternatives:

1. **LinkedIn Official API**
   - https://developer.linkedin.com/
   - Authorized access to LinkedIn data
   - Requires approval and compliance

2. **LinkedIn Sales Navigator**
   - Official prospecting tool
   - Advanced search and filtering
   - Legitimate for business use

3. **Manual Research**
   - Most compliant approach
   - Direct profile viewing
   - Export functionality built-in

4. **Third-party Tools**
   - Lusha, Hunter.io, Apollo.io
   - Legitimate data enrichment
   - Compliance-focused

---

## Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Check existing issues first
- Provide detailed error logs
- Include configuration (sanitized)

---

## Changelog

### Version 1.0.0 (2024-01-15)
- Initial release
- Basic profile scraping
- Intelligent scheduling
- Data export (JSON/CSV)
- Comprehensive logging
- Error handling

---

**Remember: Respect privacy, follow laws, and use responsibly! 🚀**