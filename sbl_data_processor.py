import os
import csv
import pandas as pd
import re

# Define the paths
TEAM_DATA_DIR = "data"
PLAYER_DATA_DIR = "data/players"
OUTPUT_DIR = "data_processed"

def process_player_data():
    """Process player statistics data"""
    print("Processing player statistics data...")
    
    # Create output directory
    os.makedirs(f"{OUTPUT_DIR}/players", exist_ok=True)
    
    # List all player CSV files
    player_files = [f for f in os.listdir(PLAYER_DATA_DIR) if f.endswith('.csv')]
    
    for file in player_files:
        # Read the CSV file
        file_path = f"{PLAYER_DATA_DIR}/{file}"
        df = pd.read_csv(file_path)
        
        # Fix player URLs (remove duplicated domain)
        if 'Player_URL' in df.columns:
            df['Player_URL'] = df['Player_URL'].apply(lambda url: 
                re.sub(r'https://hosted\.dcd\.shared\.geniussports\.comhttps://hosted\.dcd\.shared\.geniussports\.com', 
                        'https://hosted.dcd.shared.geniussports.com', 
                        url if pd.notna(url) else ""))
        
        # Write the processed data
        output_path = f"{OUTPUT_DIR}/players/{file}"
        df.to_csv(output_path, index=False)
        print(f"Processed {file} - {len(df)} player records")
    
    return len(player_files)

def process_team_data():
    """Process team statistics data"""
    print("Processing team statistics data...")
    
    # Create output directory
    os.makedirs(f"{OUTPUT_DIR}/teams", exist_ok=True)
    
    # Get all team directories
    team_dirs = [d for d in os.listdir(TEAM_DATA_DIR) 
                if os.path.isdir(f"{TEAM_DATA_DIR}/{d}") and d != "players"]
    
    teams_processed = 0
    for team_dir in team_dirs:
        # Create team directory in output
        os.makedirs(f"{OUTPUT_DIR}/teams/{team_dir}", exist_ok=True)
        
        # List all CSV files for this team
        team_files = [f for f in os.listdir(f"{TEAM_DATA_DIR}/{team_dir}") if f.endswith('.csv')]
        
        for file in team_files:
            # Read the CSV file
            file_path = f"{TEAM_DATA_DIR}/{team_dir}/{file}"
            df = pd.read_csv(file_path)
            
            # Write the processed data
            output_path = f"{OUTPUT_DIR}/teams/{team_dir}/{file}"
            df.to_csv(output_path, index=False)
        
        teams_processed += 1
        print(f"Processed team: {team_dir} - {len(team_files)} files")
    
    return teams_processed

def extract_teams_list():
    """Extract and process the teams list"""
    print("Processing teams list...")
    
    # Check if teams.csv exists
    if os.path.exists(f"{TEAM_DATA_DIR}/teams.csv"):
        # Read the CSV file
        df = pd.read_csv(f"{TEAM_DATA_DIR}/teams.csv")
        
        # Write the processed data
        output_path = f"{OUTPUT_DIR}/teams.csv"
        df.to_csv(output_path, index=False)
        print(f"Processed teams list - {len(df)} teams")
        return len(df)
    
    return 0

def main():
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Process the data
    teams_count = extract_teams_list()
    teams_processed = process_team_data()
    player_files = process_player_data()
    
    print("\n=== Summary ===")
    print(f"Teams list: {teams_count} teams")
    print(f"Team data: {teams_processed} teams processed")
    print(f"Player data: {player_files} files processed")
    print(f"Data saved to {OUTPUT_DIR} directory")

if __name__ == "__main__":
    main() 