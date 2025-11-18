# More Data Directory

This directory stores data scraped from various sources including:
- Basketball Reference (via basketball-reference-scraper)
- Kaggle datasets
- GitHub repositories
- Other external data sources

## Directory Structure

```
more/
├── schedules/          # Season schedules
├── box_scores/         # Individual game box scores
├── team_stats/         # Team statistics by season
├── player_stats/       # Player statistics
├── raw/                # Raw/unprocessed data and metadata
└── README.md           # This file
```

## Usage

### Scraping Data

Run the scraper script from the backend directory:

```bash
cd backend
python scrape_basketball_data.py
```

### Custom Scraping

```python
from scrape_basketball_data import BasketballDataScraper

scraper = BasketballDataScraper()

# Scrape a specific season schedule
scraper.scrape_season_schedule(2024)

# Scrape multiple seasons
scraper.scrape_multiple_seasons(2020, 2024)

# Scrape team stats
scraper.scrape_team_stats(2024, 'LAL')

# Scrape all teams stats for a season
scraper.scrape_all_teams_stats(2024)

# Scrape a specific box score
scraper.scrape_box_score('2024-01-15', 'LAL', 'GSW')

# Scrape box scores from schedule
scraper.scrape_from_schedule(2024, max_games=10)
```

## Data Sources

### Basketball Reference
- Schedules: All NBA games by season
- Box Scores: Detailed game statistics
- Team Stats: Season-long team statistics
- Player Stats: Individual player statistics

### Kaggle
- Place Kaggle datasets here
- Recommended: NBA datasets, betting odds, historical data

### GitHub
- Place data from GitHub repositories here
- Recommended: Open-source NBA datasets

## Notes

- All scraped data is saved as CSV files
- Metadata is stored in `raw/metadata.json`
- Rate limiting is implemented to respect API limits
- Data is organized by type and season for easy access

