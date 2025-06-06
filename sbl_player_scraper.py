import asyncio
import os
import csv
import re
from playwright.async_api import async_playwright

# URL for player statistics
PLAYER_STATS_URL = "https://hosted.dcd.shared.geniussports.com/SBF/en/competition/38899/statistics/player"

async def scrape_player_stats(page):
    """Scrape player statistics from the player statistics page"""
    print(f"Scraping player statistics from {PLAYER_STATS_URL}")
    
    # Navigate to the player statistics page
    await page.goto(PLAYER_STATS_URL, wait_until="networkidle")
    
    # Take screenshot
    os.makedirs("screenshots", exist_ok=True)
    await page.screenshot(path="screenshots/player_stats.png")
    
    # Wait for the table to load
    await page.wait_for_selector("table", timeout=30000)
    
    # Find all tables (there might be multiple tables for different stat categories)
    tables = await page.locator("table").all()
    print(f"Found {len(tables)} statistics tables")
    
    # Create data directory
    os.makedirs("data/players", exist_ok=True)
    
    # Process each table
    for table_index, table in enumerate(tables):
        # Try to determine what type of statistics this table contains
        table_header_elements = await page.locator("h4").all()
        table_header = ""
        if table_index < len(table_header_elements):
            table_header = await table_header_elements[table_index].inner_text()
        
        # Clean up the table name
        table_name = table_header.strip() if table_header else f"table_{table_index + 1}"
        table_name = re.sub(r'[^\w\s-]', '', table_name).strip().replace(' ', '_').lower()
        
        print(f"\nProcessing {table_name} table")
        
        # Get table headers
        headers = await table.locator("thead th").all_inner_texts()
        print(f"Headers: {headers}")
        
        # Get table rows
        rows = await table.locator("tbody tr").all()
        print(f"Found {len(rows)} rows (players)")
        
        # Prepare data for CSV
        csv_data = []
        
        # Process all player rows
        for row in rows:
            cells = await row.locator("td").all_inner_texts()
            
            # Extract player name and link from the first cell (it contains a link)
            player_links = await row.locator("td a").all()
            
            if len(player_links) > 0:
                player_cell = player_links[0]
                player_name = await player_cell.inner_text()
                player_url = await player_cell.get_attribute("href")
                
                # For the player name cell, replace the name+link with just the name
                cells[0] = player_name
                
                # Fix the URL
                if player_url:
                    # Extract just the path part of the URL
                    url_path = player_url.replace("https://hosted.dcd.shared.geniussports.com", "")
                    if url_path.startswith("/"):
                        url_column = f"https://hosted.dcd.shared.geniussports.com{url_path}"
                    else:
                        url_column = f"https://hosted.dcd.shared.geniussports.com/{url_path}"
                else:
                    url_column = ""
                
                # Add the row data with the URL at the end
                row_data = cells + [url_column]
                csv_data.append(row_data)
            else:
                # No player link, just add the regular data
                csv_data.append(cells + [""])  # Add empty URL column
        
        # Add URL as the last header
        headers.append("Player_URL")
        
        # Save to CSV
        csv_filename = f"data/players/{table_name}.csv"
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)  # Write headers
            writer.writerows(csv_data)  # Write data
            
        print(f"Saved {len(csv_data)} player records to {csv_filename}")
    
    return len(tables) > 0

async def main():
    # Create directories
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/players", exist_ok=True)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Scrape player statistics
        success = await scrape_player_stats(page)
        
        await browser.close()
        
        print("\n=== Summary ===")
        print("Player statistics scraping:", "Success" if success else "Failed")
        print("Data saved to data/players directory")

if __name__ == "__main__":
    asyncio.run(main()) 
