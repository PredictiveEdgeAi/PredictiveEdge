"""
Script to fetch historical odds from The Odds API.
The Odds API provides historical data since mid-2020.
"""
from src.data_ingestion import DataIngestor
from datetime import datetime, date
import sys


def main():
    """Fetch historical odds for a date range."""
    print("=" * 60)
    print("NBA Predictor - Historical Odds Fetcher")
    print("=" * 60)
    print()
    
    # Default: Fetch odds from mid-2020 to current date
    # The Odds API historical data starts around June 2020
    start_date = date(2020, 6, 1)
    end_date = datetime.now().date()
    
    # Allow command line arguments for date range
    if len(sys.argv) >= 3:
        try:
            start_date = datetime.strptime(sys.argv[1], "%Y-%m-%d").date()
            end_date = datetime.strptime(sys.argv[2], "%Y-%m-%d").date()
        except ValueError:
            print("Invalid date format. Use YYYY-MM-DD")
            print("Usage: python fetch_historical_odds.py [start_date] [end_date]")
            sys.exit(1)
    elif len(sys.argv) == 2:
        print("Please provide both start_date and end_date, or none for defaults")
        print("Usage: python fetch_historical_odds.py [start_date] [end_date]")
        sys.exit(1)
    
    print(f"Fetching historical odds from {start_date} to {end_date}")
    print("Note: This may take a while due to API rate limits.")
    print("The Odds API free plan allows 500 requests/month.")
    print()
    
    ingestor = DataIngestor()
    try:
        ingestor.fetch_historical_odds_from_api(start_date, end_date)
    except KeyboardInterrupt:
        print("\n\nFetch interrupted by user. Partial data may have been saved.")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        ingestor.close()
    
    print("\nDone!")


if __name__ == "__main__":
    main()

