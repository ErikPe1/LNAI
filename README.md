# LinkedIn AI Profile Scraper

## Overview
This tool is a LinkedIn AI Profile Scraper that uses PyAutoGUI to control the mouse. It requires manual login to your LinkedIn account and waits for 10 seconds, allowing you to switch windows before it begins navigating profiles.

## Features
- **AI Profile Navigation**: The scraper utilizes AI to navigate LinkedIn profiles automatically.
- **Scheduled Operation**: It operates only during weekdays (Monday to Friday) from 9 AM to 4:30 PM.
- **Random Delays**: Between profiles, the scraper introduces random delays of 60 to 600 seconds to mimic human behavior.
- **Data Extraction**: Data is extracted from profiles using Optical Character Recognition (OCR).
- **Output Format**: Extracted data is saved in JSON format.
- **Emergency Stop**: You can stop the scraper by pressing the ESC key.

## Installation Steps
1. **Clone the repository**:
   ```bash
   git clone https://github.com/ErikPe1/LNAI.git
   cd LNAI
   ```
2. **Install required packages**:
   Make sure you have Python installed, then run:
   ```bash
   pip install pyautogui opencv-python pytesseract numpy
   ```
3. **Set up Tesseract OCR**:
   Download and install Tesseract OCR, and ensure the path to the installation is included in your system's PATH environment variable.

## Usage Instructions
1. **Log in to LinkedIn**: Open LinkedIn in your browser and log in to your account.
2. **Switch windows**: Once logged in, switch back to the application running the scraper. You have 10 seconds to do this.
3. **Start the scraper**: Run the scraper script.
4. **Observe the AI in action**: The AI will now navigate through profiles and extract the data.
5. **Stop the process**: If you wish to stop the execution at any time, just press the ESC key.

## Legal Disclaimer
Using automated tools like this may violate LinkedIn's Terms of Service. Proceed at your own risk and ensure you understand the legal implications of scraping data from LinkedIn.

## Troubleshooting Tips
- **Script Not Running**: Ensure all dependencies are installed and your Python environment is set up correctly.
- **Data Not Extracting Properly**: Verify that the OCR setup is correctly configured and that Tesseract is accessible.
- **Mouse Control Issues**: Check if PyAutoGUI has permission to control the mouse on your system. Some operating systems and settings may prevent it.

For further assistance or to report issues, please open an issue in this repository or contact the maintainer.