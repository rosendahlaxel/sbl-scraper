from playwright.sync_api import sync_playwright
from scraper import SBLScraper
import json
import os

def main():
    with sync_playwright() as playwright:
        # Launch the browser
        browser = playwright.chromium.launch(headless=False)
        page = browser.new_page()
        
        # Initialize scraper
        scraper = SBLScraper(page)
        
        # Navigate to homepage
        title = scraper.navigate_to_homepage()
        print(f"Page title: {title}")
        
        # Extract data
        data = scraper.extract_data()
        
        # Save data
        os.makedirs("data", exist_ok=True)
        with open("data/output.json", "w") as f:
            json.dump(data, f, indent=2)
            
        # Take screenshot
        os.makedirs("screenshots", exist_ok=True)
        page.screenshot(path="screenshots/homepage.png")
        
        # Close browser
        browser.close()

if __name__ == "__main__":
    main()