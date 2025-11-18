"""
Example scripts for scraping basketball data.
Use these as templates for your own scraping needs.
"""
from scrape_basketball_data import BasketballDataScraper
from datetime import datetime, timedelta
import time
import pandas as pd


def example_1_scrape_recent_seasons():
    """Scrape schedules for recent seasons."""
    scraper = BasketballDataScraper()
    
    # Scrape last 5 seasons
    current_year = datetime.now().year
    scraper.scrape_multiple_seasons(current_year - 5, current_year)


def example_2_scrape_current_season():
    """Scrape current season data."""
    scraper = BasketballDataScraper()
    current_year = datetime.now().year
    
    # Scrape current season schedule
    scraper.scrape_season_schedule(current_year)
    
    # Scrape all team stats
    scraper.scrape_all_teams_stats(current_year)


def example_3_scrape_specific_games():
    """Scrape box scores for specific games."""
    scraper = BasketballDataScraper()
    
    # Example: Scrape Lakers vs Warriors games
    games = [
        ('2024-01-15', 'LAL', 'GSW'),
        ('2024-02-10', 'GSW', 'LAL'),
    ]
    
    for date, team1, team2 in games:
        scraper.scrape_box_score(date, team1, team2)
        time.sleep(2)  # Rate limiting


def example_4_scrape_playoff_games():
    """Scrape playoff games for a season."""
    scraper = BasketballDataScraper()
    season = 2024
    
    # Get schedule
    schedule_df = scraper.scrape_season_schedule(season)
    
    if schedule_df is not None:
        # Filter for playoff games (usually in April-June)
        playoff_games = schedule_df[
            (schedule_df['DATE'].str.contains('Apr|May|Jun', case=False, na=False))
        ]
        
        print(f"Found {len(playoff_games)} playoff games")
        
        # Scrape box scores
        for idx, row in playoff_games.head(10).iterrows():  # Limit to 10 games
            try:
                date_str = row.get('DATE', '')
                date_obj = pd.to_datetime(date_str)
                date_formatted = date_obj.strftime('%Y-%m-%d')
                
                visitor = str(row.get('VISITOR', '')).strip()
                home = str(row.get('HOME', '')).strip()
                
                scraper.scrape_box_score(date_formatted, visitor, home)
                time.sleep(2)
            except Exception as e:
                print(f"Error: {e}")


def example_5_scrape_team_comparison():
    """Scrape stats for multiple teams to compare."""
    scraper = BasketballDataScraper()
    season = 2024
    
    teams = ['LAL', 'GSW', 'BOS', 'MIA', 'MIL']
    
    for team in teams:
        scraper.scrape_team_stats(season, team)
        time.sleep(1)


def example_6_batch_scrape_recent_games():
    """Scrape box scores for recent games."""
    scraper = BasketballDataScraper()
    
    # Get current season
    current_year = datetime.now().year
    schedule_df = scraper.scrape_season_schedule(current_year)
    
    if schedule_df is not None:
        # Get games from last 30 days
        today = datetime.now()
        thirty_days_ago = today - timedelta(days=30)
        
        recent_games = []
        for idx, row in schedule_df.iterrows():
            try:
                date_str = row.get('DATE', '')
                if not date_str:
                    continue
                
                date_obj = pd.to_datetime(date_str)
                if date_obj >= thirty_days_ago:
                    recent_games.append(row)
            except:
                continue
        
        print(f"Found {len(recent_games)} games in last 30 days")
        
        # Scrape box scores
        for row in recent_games[:20]:  # Limit to 20 games
            try:
                date_str = row.get('DATE', '')
                date_obj = pd.to_datetime(date_str)
                date_formatted = date_obj.strftime('%Y-%m-%d')
                
                visitor = str(row.get('VISITOR', '')).strip()
                home = str(row.get('HOME', '')).strip()
                
                scraper.scrape_box_score(date_formatted, visitor, home)
                time.sleep(2)
            except Exception as e:
                print(f"Error: {e}")


if __name__ == "__main__":
    print("Basketball Data Scraping Examples")
    print("=" * 60)
    print()
    print("Uncomment the example you want to run:")
    print()
    print("# Example 1: Scrape recent seasons")
    print("# example_1_scrape_recent_seasons()")
    print()
    print("# Example 2: Scrape current season")
    print("# example_2_scrape_current_season()")
    print()
    print("# Example 3: Scrape specific games")
    print("# example_3_scrape_specific_games()")
    print()
    print("# Example 4: Scrape playoff games")
    print("# example_4_scrape_playoff_games()")
    print()
    print("# Example 5: Scrape team comparison")
    print("# example_5_scrape_team_comparison()")
    print()
    print("# Example 6: Batch scrape recent games")
    print("# example_6_batch_scrape_recent_games()")

