import os
import asyncio
import subprocess
import time

def run_command(command):
    """Run a command and print its output"""
    print(f"Running: {command}")
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    
    # Print output in real-time
    for line in iter(process.stdout.readline, b''):
        print(line.decode().strip())
    
    process.wait()
    return process.returncode

def main():
    print("=== SBL Scraper - All Data ===")
    
    start_time = time.time()
    
    # Step 1: Scrape team statistics
    print("\n\n=== Step 1: Scraping Team Statistics ===")
    result = run_command("python sbl_team_scraper.py")
    if result != 0:
        print("ERROR: Team scraper failed!")
        return
    
    # Step 2: Scrape player statistics
    print("\n\n=== Step 2: Scraping Player Statistics ===")
    result = run_command("python sbl_player_scraper.py")
    if result != 0:
        print("ERROR: Player scraper failed!")
        return
    
    # Step 3: Process all data
    print("\n\n=== Step 3: Processing All Data ===")
    result = run_command("python sbl_data_processor.py")
    if result != 0:
        print("ERROR: Data processor failed!")
        return
    
    # Calculate runtime
    end_time = time.time()
    duration = end_time - start_time
    minutes = int(duration / 60)
    seconds = int(duration % 60)
    
    print("\n\n=== Scraping Complete ===")
    print(f"Runtime: {minutes} minutes and {seconds} seconds")
    print("All data has been scraped and processed successfully!")
    print(f"Data is available in the 'data_processed' directory")

if __name__ == "__main__":
    main() 