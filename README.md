# SBL Scraper

A web scraper for extracting data from the Swedish Basketball League (SBL) website using Playwright.

## Features

- Scrape team statistics from individual team pages
- Scrape player statistics from the league statistics page
- Process and organize data into CSV files

## Setup

1. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install Playwright browsers:
```bash
python -m playwright install
```

## Usage

### All-in-One Scraping

To run all scrapers and process the data in one command:

```bash
python scrape_all.py
```

This will:
1. Scrape team statistics
2. Scrape player statistics
3. Process and organize all data
4. Save results to the `data_processed` directory

### Individual Scripts

If you prefer to run the scripts individually:

#### Scrape Team Statistics

The script iterates through all team pages and extracts team statistics:

```bash
python sbl_team_scraper.py
```

This will create:
- `data/teams.csv` - A list of all teams with their IDs
- `data/[TeamName]/` - Folders for each team containing:
  - `averages.csv` - Player averages
  - `totals.csv` - Player totals
  - `minutes.csv` - Minutes played

#### Scrape Player Statistics

Extract player statistics from the league statistics page:

```bash
python sbl_player_scraper.py
```

This will create:
- `data/players/` - Contains player statistics files:
  - `averages.csv` - Player averages
  - `shooting_statistics.csv` - Shooting statistics
  - `table_3.csv` - Additional statistics

#### Process Data

Process and clean up the collected data:

```bash
python sbl_data_processor.py
```

This will create:
- `data_processed/` - Contains processed data:
  - `teams.csv` - Team information
  - `teams/` - Team statistics
  - `players/` - Player statistics

## Data Files

### Teams Data

Each team has the following data files:

- `totals.csv` - Season totals for each player on the team
- `averages.csv` - Per-game averages for each player on the team
- `minutes.csv` - Minutes played for each player on the team

### Players Data

The player statistics are organized in these files:

- `averages.csv` - Per-game averages for all players in the league
- `shooting_statistics.csv` - Shooting percentages and attempts
- `table_3.csv` - Additional statistics like games played, plus/minus
