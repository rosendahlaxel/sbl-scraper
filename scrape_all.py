"""Orchestrate SBL data collection."""

import asyncio
import time

from sbl_team_scraper import main as scrape_teams
from sbl_player_scraper import main as scrape_players
from sbl_data_processor import main as process_data


async def run_pipeline() -> None:
    """Run the full scraping pipeline."""
    print("=== SBL Scraper - All Data ===")

    start_time = time.time()

    print("\n\n=== Step 1: Scraping Team Statistics ===")
    await scrape_teams()

    print("\n\n=== Step 2: Scraping Player Statistics ===")
    await scrape_players()

    print("\n\n=== Step 3: Processing All Data ===")
    process_data()

    duration = time.time() - start_time
    minutes = int(duration / 60)
    seconds = int(duration % 60)

    print("\n\n=== Scraping Complete ===")
    print(f"Runtime: {minutes} minutes and {seconds} seconds")
    print("All data has been scraped and processed successfully!")
    print("Data is available in the 'data_processed' directory")


def main() -> None:
    asyncio.run(run_pipeline())


if __name__ == "__main__":

    main()
