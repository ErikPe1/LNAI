# LNAI - LinkedIn AI Profile Scraper

Automated LinkedIn profile scraping with intelligent scheduling and data extraction.

## ⚠️ IMPORTANT LEGAL DISCLAIMER

**THIS TOOL IS FOR EDUCATIONAL PURPOSES ONLY.** Web scraping LinkedIn may violate their Terms of Service. Always use LinkedIn's official API for legitimate use cases.

## Features

- ✅ Automated profile navigation and data extraction
- ✅ Time-based scheduling (Monday-Friday, 9:00 AM - 4:30 PM)
- ✅ Random delays (60-600 seconds) between profiles to mimic human behavior
- ✅ Comprehensive data extraction (name, headline, experience, education, skills, certifications, languages)
- ✅ JSON and CSV data storage
- ✅ Duplicate prevention
- ✅ Robust error handling and logging

## Installation

### Prerequisites
- Python 3.9 or higher
- Chrome browser
- LinkedIn account

### Install from source

```bash
# Clone the repository
git clone https://github.com/ErikPe1/LNAI.git
cd LNAI

# Install dependencies
pip install -r requirements.txt

# Or install in development mode (recommended for development)
pip install -e .

# Or install with development tools
pip install -e ".[dev]"
```

## Quick Start

```bash
# Install the package
pip install -r requirements.txt

# Or install in development mode
pip install -e .

# Configure credentials
cp linkedin_scraper/.env.example .env
# Edit .env with your LinkedIn credentials

# Run the scraper
python -m linkedin_scraper.scraper

# Or run tests
python linkedin_scraper/test_scraper.py
```

## Documentation

See [linkedin_scraper/README.md](linkedin_scraper/README.md) for complete documentation including:
- Installation instructions
- Usage examples
- Configuration options
- Data formats
- Troubleshooting guide

## Project Structure

```
linkedin_scraper/
├── scraper.py              # Main scraper logic
├── profile_extractor.py    # Profile data extraction
├── scheduler.py            # Time-based scheduling
├── config.py               # Configuration constants
├── requirements.txt        # Python dependencies
├── .env.example            # Example environment variables
├── README.md               # Detailed documentation
└── data/                   # Data storage directory
```

## Legal Notice

Always respect website terms of service, robots.txt, and data privacy laws. Use LinkedIn's official API for production applications.