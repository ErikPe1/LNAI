#Scraper

Automation script with coordinate-driven click flow and screenshot/OCR extraction.

## Setup
```bash
pip install -r linkedin_scraper/requirements.txt
```

## Configure
Edit `linkedin_scraper/config.py`:
- `ARROW_BUTTON_X = 1850`
- `ARROW_BUTTON_Y = 311`
- update `PROFILE_CARD_POSITIONS` if needed for your screen

## Run
```bash
python linkedin_scraper/scraper.py
```

Press `ESC` to stop safely.
Outputs:
- `screenshots/`
- `Account_Outputs/`
- `linkedin_scraper.log`
