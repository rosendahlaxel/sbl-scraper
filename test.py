import asyncio
import os
import csv
from playwright.async_api import async_playwright

URL = "https://hosted.dcd.shared.geniussports.com/SBF/en/competition/38899/team/175103/statistics"

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Set to False to see the browser
        page = await browser.new_page()
        
        print(f"Navigating to {URL}")
        await page.goto(URL, wait_until="networkidle")
        
        # Take screenshot to see what's loading
        os.makedirs("screenshots", exist_ok=True)
        await page.screenshot(path="screenshots/debug.png")
        
        print("Page loaded, waiting for tables...")
        
        # Wait for the first table with class containing "team-stats"
        await page.wait_for_selector("table.team-stats", timeout=60000)
        
        # Process all tables with team-stats class
        tables = await page.locator("table.team-stats").all()
        print(f"Found {len(tables)} team stats tables")
        
        # Create data directory if it doesn't exist
        os.makedirs("data", exist_ok=True)
        
        for table_index, table in enumerate(tables):
            print(f"\nProcessing Table {table_index + 1}:")
            
            # Get table headers
            headers = await table.locator("thead th").all_inner_texts()
            print(f"Headers: {headers}")
            
            # Get table rows
            rows = await table.locator("tbody tr").all()
            print(f"Found {len(rows)} rows")
            
            # Prepare data for CSV
            csv_data = []
            
            # Process all rows
            for row in rows:
                cells = await row.locator("td").all_inner_texts()
                csv_data.append(cells)
                
            # Save to CSV
            csv_filename = f"data/table_{table_index + 1}.csv"
            with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)  # Write headers
                writer.writerows(csv_data)  # Write data
                
            print(f"Saved data to {csv_filename}")
        
        await browser.close()
        
        print("\nSummary:")
        print(f"Successfully scraped {len(tables)} tables from {URL}")
        print("Data saved to CSV files in the data directory")

asyncio.run(run())