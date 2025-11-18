"""
Basketball Data Scraper
Uses basketball-reference-scraper to fetch data from various sources.
Stores data in the 'more' folder for later use.
"""
import os
import pandas as pd
from pathlib import Path
from datetime import datetime
from basketball_reference_scraper.seasons import get_schedule
from basketball_reference_scraper.box_scores import get_box_scores
from basketball_reference_scraper.teams import get_team_stats
import time
import json

# Setup paths
PROJECT_ROOT = Path(__file__).parent.parent
MORE_DATA_DIR = PROJECT_ROOT / "more"
MORE_DATA_DIR.mkdir(exist_ok=True)

# Create subdirectories for organization
SCHEDULES_DIR = MORE_DATA_DIR / "schedules"
BOX_SCORES_DIR = MORE_DATA_DIR / "box_scores"
TEAM_STATS_DIR = MORE_DATA_DIR / "team_stats"
PLAYER_STATS_DIR = MORE_DATA_DIR / "player_stats"
RAW_DATA_DIR = MORE_DATA_DIR / "raw"

for dir_path in [SCHEDULES_DIR, BOX_SCORES_DIR, TEAM_STATS_DIR, PLAYER_STATS_DIR, RAW_DATA_DIR]:
    dir_path.mkdir(exist_ok=True)


class BasketballDataScraper:
    """Scraper for basketball-reference data."""
    
    def __init__(self):
        self.base_dir = MORE_DATA_DIR
        print(f"Data will be saved to: {self.base_dir}")
    
    def scrape_season_schedule(self, season: int, save_csv: bool = True):
        """
        Scrape season schedule for a given year.
        
        Args:
            season: Year of the season (e.g., 2024 for 2023-2024 season)
            save_csv: Whether to save as CSV
        """
        print(f"Scraping schedule for {season} season...")
        try:
            df = get_schedule(season)
            
            if df is None or df.empty:
                print(f"No data found for {season} season")
                return None
            
            if save_csv:
                csv_path = SCHEDULES_DIR / f"schedule_{season}.csv"
                df.to_csv(csv_path, index=False)
                print(f"✓ Saved schedule to {csv_path}")
            
            return df
            
        except Exception as e:
            print(f"Error scraping schedule for {season}: {e}")
            return None
    
    def scrape_multiple_seasons(self, start_season: int, end_season: int):
        """Scrape schedules for multiple seasons."""
        print(f"Scraping schedules from {start_season} to {end_season}...")
        all_schedules = []
        
        for season in range(start_season, end_season + 1):
            df = self.scrape_season_schedule(season)
            if df is not None:
                df['season'] = season
                all_schedules.append(df)
            time.sleep(1)  # Rate limiting
        
        # Combine all schedules
        if all_schedules:
            combined = pd.concat(all_schedules, ignore_index=True)
            combined_path = SCHEDULES_DIR / f"all_schedules_{start_season}_{end_season}.csv"
            combined.to_csv(combined_path, index=False)
            print(f"✓ Saved combined schedules to {combined_path}")
            return combined
        
        return None
    
    def scrape_box_score(self, date: str, team1: str, team2: str, save_csv: bool = True):
        """
        Scrape box score for a specific game.
        
        Args:
            date: Date in format 'YYYY-MM-DD'
            team1: First team abbreviation (e.g., 'LAL')
            team2: Second team abbreviation (e.g., 'GSW')
            save_csv: Whether to save as CSV
        """
        print(f"Scraping box score: {team1} vs {team2} on {date}...")
        try:
            df = get_box_scores(date, team1, team2)
            
            if df is None or df.empty:
                print(f"No box score data found")
                return None
            
            if save_csv:
                filename = f"box_score_{date}_{team1}_{team2}.csv"
                csv_path = BOX_SCORES_DIR / filename
                df.to_csv(csv_path, index=True)
                print(f"✓ Saved box score to {csv_path}")
            
            return df
            
        except Exception as e:
            print(f"Error scraping box score: {e}")
            return None
    
    def scrape_team_stats(self, season: int, team_abbr: str, save_csv: bool = True):
        """
        Scrape team statistics for a season.
        Note: This uses the teams module - adjust based on library version.
        
        Args:
            season: Year of the season
            team_abbr: Team abbreviation (e.g., 'LAL')
            save_csv: Whether to save as CSV
        """
        print(f"Scraping team stats for {team_abbr} in {season}...")
        try:
            # Get team stats
            stats = get_team_stats(team_abbr, season)
            
            if stats is None:
                print(f"No stats found for {team_abbr}")
                return None
            
            if save_csv:
                filename = f"team_stats_{team_abbr}_{season}.csv"
                csv_path = TEAM_STATS_DIR / filename
                if isinstance(stats, pd.DataFrame):
                    stats.to_csv(csv_path, index=False)
                elif isinstance(stats, pd.Series):
                    # Convert Series to DataFrame
                    df = stats.to_frame().T
                    df.to_csv(csv_path, index=False)
                else:
                    # If it's a dict or other format, convert to DataFrame
                    df = pd.DataFrame([stats])
                    df.to_csv(csv_path, index=False)
                print(f"✓ Saved team stats to {csv_path}")
            
            return stats
            
        except Exception as e:
            print(f"Error scraping team stats: {e}")
            print("Note: Team stats scraping may require different method based on library version")
            return None
    
    def scrape_all_teams_stats(self, season: int):
        """Scrape stats for all NBA teams in a season."""
        print(f"Scraping stats for all teams in {season} season...")
        
        # Common NBA team abbreviations
        team_abbreviations = [
            'ATL', 'BOS', 'BKN', 'CHA', 'CHI', 'CLE', 'DAL', 'DEN',
            'DET', 'GSW', 'HOU', 'IND', 'LAC', 'LAL', 'MEM', 'MIA',
            'MIL', 'MIN', 'NOP', 'NYK', 'OKC', 'ORL', 'PHI', 'PHX',
            'POR', 'SAC', 'SAS', 'TOR', 'UTA', 'WAS'
        ]
        
        all_stats = []
        for team in team_abbreviations:
            stats = self.scrape_team_stats(season, team, save_csv=True)
            if stats is not None:
                stats['team'] = team
                stats['season'] = season
                all_stats.append(stats)
            time.sleep(0.5)  # Rate limiting
        
        if all_stats:
            combined = pd.concat(all_stats, ignore_index=True)
            combined_path = TEAM_STATS_DIR / f"all_teams_stats_{season}.csv"
            combined.to_csv(combined_path, index=False)
            print(f"✓ Saved combined team stats to {combined_path}")
            return combined
        
        return None
    
    def scrape_player_stats(self, player_name: str, season: int = None, save_csv: bool = True):
        """
        Scrape player statistics.
        Note: Player stats may require different library or API.
        
        Args:
            player_name: Full player name (e.g., 'LeBron James')
            season: Optional season year
            save_csv: Whether to save as CSV
        """
        print(f"Scraping stats for {player_name}...")
        print("Note: Player stats scraping may require additional setup")
        print("Check basketball-reference-scraper documentation for player stats API")
        
        # Placeholder - implement based on available library methods
        # You may need to use a different library or API for player stats
        return None
    
    def scrape_from_schedule(self, season: int, max_games: int = None):
        """
        Scrape box scores for all games in a season schedule.
        
        Args:
            season: Year of the season
            max_games: Maximum number of games to scrape (None for all)
        """
        print(f"Scraping box scores from {season} schedule...")
        
        # Get schedule first
        schedule_df = self.scrape_season_schedule(season, save_csv=True)
        
        if schedule_df is None or schedule_df.empty:
            print("No schedule data available")
            return
        
        games_scraped = 0
        for idx, row in schedule_df.iterrows():
            if max_games and games_scraped >= max_games:
                break
            
            try:
                date_str = row.get('DATE', '')
                if not date_str:
                    continue
                
                # Parse date
                try:
                    date_obj = pd.to_datetime(date_str)
                    date_formatted = date_obj.strftime('%Y-%m-%d')
                except:
                    continue
                
                visitor = str(row.get('VISITOR', '')).strip()
                home = str(row.get('HOME', '')).strip()
                
                if not visitor or not home:
                    continue
                
                # Scrape box score
                self.scrape_box_score(date_formatted, visitor, home)
                games_scraped += 1
                
                # Rate limiting
                time.sleep(2)
                
            except Exception as e:
                print(f"Error processing game {idx}: {e}")
                continue
        
        print(f"✓ Scraped {games_scraped} games from {season} season")
    
    def save_metadata(self, data_type: str, info: dict):
        """Save metadata about scraped data."""
        metadata_path = RAW_DATA_DIR / "metadata.json"
        
        if metadata_path.exists():
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
        else:
            metadata = {}
        
        if data_type not in metadata:
            metadata[data_type] = []
        
        info['scraped_at'] = datetime.now().isoformat()
        metadata[data_type].append(info)
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def get_summary(self):
        """Get summary of scraped data."""
        summary = {
            'schedules': len(list(SCHEDULES_DIR.glob('*.csv'))),
            'box_scores': len(list(BOX_SCORES_DIR.glob('*.csv'))),
            'team_stats': len(list(TEAM_STATS_DIR.glob('*.csv'))),
            'player_stats': len(list(PLAYER_STATS_DIR.glob('*.csv'))),
        }
        
        print("\n" + "=" * 60)
        print("Scraped Data Summary")
        print("=" * 60)
        print(f"Schedules: {summary['schedules']} files")
        print(f"Box Scores: {summary['box_scores']} files")
        print(f"Team Stats: {summary['team_stats']} files")
        print(f"Player Stats: {summary['player_stats']} files")
        print("=" * 60)
        
        return summary


def main():
    """Main function with example usage."""
    scraper = BasketballDataScraper()
    
    print("=" * 60)
    print("Basketball Data Scraper")
    print("=" * 60)
    print()
    
    # Example 1: Scrape recent season schedules
    print("Example 1: Scraping recent season schedules...")
    current_year = datetime.now().year
    scraper.scrape_multiple_seasons(current_year - 2, current_year)
    print()
    
    # Example 2: Scrape a few box scores (limited to avoid rate limits)
    print("Example 2: Scraping sample box scores...")
    scraper.scrape_from_schedule(current_year, max_games=5)
    print()
    
    # Show summary
    scraper.get_summary()
    
    print("\n✓ Scraping complete!")
    print(f"Data saved to: {MORE_DATA_DIR}")
    print("\nNote: Team stats and player stats may require additional setup.")
    print("Focus on schedules and box scores for now.")


if __name__ == "__main__":
    main()

