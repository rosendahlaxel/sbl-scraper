import asyncio
import os
import csv
import re
from playwright.async_api import async_playwright

# Base URLs
TEAMS_URL = "https://hosted.dcd.shared.geniussports.com/SBF/en/competition/38899/teams"
TEAM_STATS_URL_TEMPLATE = "https://hosted.dcd.shared.geniussports.com/SBF/en/competition/38899/team/{team_id}/statistics"

# Manual mapping of team IDs to names based on the search results
TEAM_NAMES = {
    "175102": "BC Luleå",
    "175103": "Borås Basket",
    "175104": "Nässjö Basket",
    "175105": "Högsbo Basket",
    "175106": "Jämtland Basket",
    "175107": "Köping Stars",
    "175108": "Norrköping Dolphins",
    "175109": "Södertälje BBK",
    "175110": "Umeå BSKT",
    "175111": "Uppsala Basket"
}

async def extract_team_links(page):
    """Extract team links from the teams page"""
    print(f"Extracting team links from {TEAMS_URL}")
    await page.goto(TEAMS_URL, wait_until="networkidle")
    
    # Take screenshot of teams page
    await page.screenshot(path="screenshots/teams_page.png")
    
    # Find all team links and names
    # The teams are listed in a section with team names followed by links
    team_elements = await page.locator("div.teams a").all()
    
    teams = []
    for element in team_elements:
        href = await element.get_attribute("href")
        if href and "/team/" in href:
            team_id_match = re.search(r'/team/(\d+)', href)
            if team_id_match:
                team_id = team_id_match.group(1)
                # Get the text content which should be the team name
                team_name = await element.inner_text()
                
                # Clean up the team name
                team_name = team_name.strip()
                
                # Only add if we have a valid team name
                if team_name:
                    teams.append({
                        "id": team_id,
                        "name": team_name,
                        "url": f"https://hosted.dcd.shared.geniussports.com{href}"
                    })
    
    # Remove duplicates based on team_id
    unique_teams = []
    seen_ids = set()
    for team in teams:
        if team["id"] not in seen_ids:
            seen_ids.add(team["id"])
            unique_teams.append(team)
    
    print(f"Found {len(unique_teams)} unique teams")
    return unique_teams

async def get_team_name_from_page(page, team_id):
    """Extract team name from the statistics page or use the manual mapping"""
    # First try to get from our manual mapping
    if team_id in TEAM_NAMES:
        return TEAM_NAMES[team_id]
    
    try:
        # Look for the team name in the header
        team_name_element = await page.locator("h1").first
        if team_name_element:
            team_name = await team_name_element.inner_text()
            return team_name.strip()
    except:
        pass
    
    return f"Team_{team_id}"

async def scrape_team_stats(page, team):
    """Scrape statistics for a specific team"""
    team_id = team["id"]
    stats_url = TEAM_STATS_URL_TEMPLATE.format(team_id=team_id)
    
    print(f"\nScraping statistics for team ID: {team_id}")
    print(f"URL: {stats_url}")
    
    await page.goto(stats_url, wait_until="networkidle")
    
    # Get the team name from the page if not available
    team_name = team["name"]
    if not team_name or team_name.strip() == "":
        team_name = await get_team_name_from_page(page, team_id)
    
    print(f"Team name: {team_name}")
    
    # Create team directory with sanitized name
    sanitized_name = re.sub(r'[^\w\s-]', '', team_name).strip().replace(' ', '_')
    team_dir = f"data/{sanitized_name}"
    os.makedirs(team_dir, exist_ok=True)
    
    # Take screenshot
    await page.screenshot(path=f"screenshots/{sanitized_name}_stats.png")
    
    # Wait for tables to load
    try:
        await page.wait_for_selector("table.team-stats", timeout=30000)
        
        # Process all tables with team-stats class
        tables = await page.locator("table.team-stats").all()
        print(f"Found {len(tables)} statistics tables")
        
        table_names = ["totals", "per_game", "shooting"]
        
        for table_index, table in enumerate(tables):
            table_name = table_names[table_index] if table_index < len(table_names) else f"table_{table_index + 1}"
            print(f"Processing {table_name} table")
            
            # Get table headers
            headers = await table.locator("thead th").all_inner_texts()
            
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
            csv_filename = f"{team_dir}/{table_name}.csv"
            with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)  # Write headers
                writer.writerows(csv_data)  # Write data
                
            print(f"Saved data to {csv_filename}")
        
        # Update team info with the correct name
        team["name"] = team_name
        
        return True
    except Exception as e:
        print(f"Error scraping team {team_id}: {e}")
        return False

async def main():
    # Create directories
    os.makedirs("data", exist_ok=True)
    os.makedirs("screenshots", exist_ok=True)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Extract team links
        teams = await extract_team_links(page)
        
        # If no teams were found automatically, use manual team IDs
        if not teams:
            print("No teams found automatically. Using manual team IDs.")
            # These are the team IDs you mentioned (from 02 to 10)
            team_ids = ["175102", "175103", "175104", "175105", "175106", 
                       "175107", "175108", "175109", "175110", "175111"]
            
            teams = [{"id": team_id, "name": TEAM_NAMES.get(team_id, ""), 
                     "url": TEAM_STATS_URL_TEMPLATE.format(team_id=team_id)} 
                    for team_id in team_ids]
        
        # Scrape each team's statistics
        successful = 0
        failed = 0
        
        for team in teams:
            success = await scrape_team_stats(page, team)
            if success:
                successful += 1
            else:
                failed += 1
        
        # Save updated teams list with correct names
        with open("data/teams.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Name", "URL"])
            for team in teams:
                writer.writerow([team["id"], team["name"], team["url"]])
        
        await browser.close()
        
        print("\n=== Summary ===")
        print(f"Total teams: {len(teams)}")
        print(f"Successfully scraped: {successful}")
        print(f"Failed: {failed}")
        print(f"Data saved to data directory")

if __name__ == "__main__":
    asyncio.run(main()) 
