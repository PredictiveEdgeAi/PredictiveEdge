# Basketball Data Scraping Guide

## Quick Start

### Run the Scraper

```bash
cd backend
python scrape_basketball_data.py
```

This will:
- Scrape recent season schedules (last 2 years)
- Scrape sample box scores (5 games)
- Save all data to the `more/` folder

## Directory Structure

```
more/
├── schedules/          # Season schedules (CSV files)
├── box_scores/         # Individual game box scores (CSV files)
├── team_stats/         # Team statistics by season (CSV files)
├── player_stats/       # Player statistics (CSV files)
├── raw/                # Raw data and metadata
└── README.md           # Documentation
```

## Usage Examples

### 1. Scrape a Single Season Schedule

```python
from scrape_basketball_data import BasketballDataScraper

scraper = BasketballDataScraper()
scraper.scrape_season_schedule(2024)
```

### 2. Scrape Multiple Seasons

```python
scraper = BasketballDataScraper()
scraper.scrape_multiple_seasons(2020, 2024)
```

### 3. Scrape a Specific Game Box Score

```python
scraper = BasketballDataScraper()
scraper.scrape_box_score('2024-01-15', 'LAL', 'GSW')
```

### 4. Scrape All Box Scores from a Season

```python
scraper = BasketballDataScraper()
scraper.scrape_from_schedule(2024, max_games=50)  # Limit to 50 games
```

### 5. Scrape Team Stats

```python
scraper = BasketballDataScraper()
scraper.scrape_team_stats(2024, 'LAL')  # Lakers stats for 2024
```

### 6. Scrape All Teams Stats

```python
scraper = BasketballDataScraper()
scraper.scrape_all_teams_stats(2024)
```

## Rate Limiting

The scraper includes rate limiting to respect Basketball Reference's servers:
- 1-2 second delays between requests
- Adjustable delays in the code

## Data Formats

### Schedule CSV
- Columns: DATE, VISITOR, HOME, VISITOR_PTS, HOME_PTS, etc.
- One row per game

### Box Score CSV
- Index: Player names
- Columns: FG, FGA, FG%, 3P, 3PA, 3P%, FT, FTA, FT%, ORB, DRB, TRB, AST, STL, BLK, TOV, PF, PTS, +/-

### Team Stats CSV
- Team statistics aggregated by season
- Various statistical categories

## Tips

1. **Start Small**: Test with a few games/seasons first
2. **Respect Rate Limits**: Don't scrape too aggressively
3. **Save Progress**: Data is automatically saved as you scrape
4. **Check Metadata**: See `raw/metadata.json` for scraping history

## Adding Data from Other Sources

### Kaggle Datasets
1. Download dataset from Kaggle
2. Place in `more/kaggle/` folder
3. Update metadata

### GitHub Repositories
1. Clone/download repository
2. Extract relevant data
3. Place in `more/github/` folder

## Troubleshooting

### Import Errors
Make sure basketball-reference-scraper is installed:
```bash
pip install basketball-reference-scraper
```

### No Data Found
- Check if the season/game exists
- Verify team abbreviations are correct
- Check your internet connection

### Rate Limiting
If you get blocked:
- Increase delays between requests
- Scrape in smaller batches
- Wait before resuming

