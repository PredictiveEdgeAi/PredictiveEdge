"""
Test script to check what data we can actually scrape.
"""
from basketball_reference_scraper.box_scores import get_box_scores
from basketball_reference_scraper.teams import get_team_stats
import pandas as pd
from datetime import datetime, timedelta

print("=" * 60)
print("Testing Basketball Reference Scraper")
print("=" * 60)
print()

# Test 1: Box Scores
print("Test 1: Scraping a recent box score...")
try:
    # Try a recent game date
    test_date = '2024-01-15'
    df = get_box_scores(test_date, 'LAL', 'GSW')
    if isinstance(df, pd.DataFrame) and not df.empty:
        print(f"✓ Success! Box score shape: {df.shape}")
        print(f"  Columns: {df.columns.tolist()}")
        print(f"  First few rows:")
        print(df.head())
    else:
        print("✗ No data returned")
except Exception as e:
    print(f"✗ Error: {e}")

print()

# Test 2: Team Stats
print("Test 2: Scraping team stats...")
try:
    stats = get_team_stats('LAL', 2024)
    if stats is not None:
        if isinstance(stats, pd.DataFrame):
            print(f"✓ Success! Stats shape: {stats.shape}")
            print(f"  Columns: {stats.columns.tolist()}")
            print(f"  First few rows:")
            print(stats.head())
        else:
            print(f"✓ Success! Stats type: {type(stats)}")
            print(f"  Stats: {stats}")
    else:
        print("✗ No data returned")
except Exception as e:
    print(f"✗ Error: {e}")

print()
print("=" * 60)

