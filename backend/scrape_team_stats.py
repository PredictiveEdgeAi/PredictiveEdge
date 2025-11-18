"""
Quick script to scrape team stats for multiple teams and seasons.
"""
from scrape_basketball_data import BasketballDataScraper
import time

def scrape_team_stats_batch():
    """Scrape team stats for multiple teams."""
    scraper = BasketballDataScraper()
    
    # Common NBA teams
    teams = ['LAL', 'GSW', 'BOS', 'MIA', 'MIL', 'DEN', 'PHX', 'DAL', 'PHI', 'NYK']
    season = 2024
    
    print("=" * 60)
    print("Scraping Team Stats")
    print("=" * 60)
    print()
    
    successful = 0
    failed = 0
    
    for team in teams:
        try:
            print(f"Scraping {team}...")
            stats = scraper.scrape_team_stats(season, team, save_csv=True)
            if stats is not None:
                successful += 1
            else:
                failed += 1
            time.sleep(2)  # Rate limiting
        except Exception as e:
            print(f"  Error: {e}")
            failed += 1
            time.sleep(1)
    
    print()
    print("=" * 60)
    print(f"Scraping complete!")
    print(f"  Successful: {successful}")
    print(f"  Failed: {failed}")
    print("=" * 60)
    
    # Show summary
    scraper.get_summary()

if __name__ == "__main__":
    scrape_team_stats_batch()

