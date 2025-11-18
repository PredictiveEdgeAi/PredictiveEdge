"""
Example usage script for NBA Predictor.
Demonstrates how to use the various components.
"""
from src.database import get_session, init_database
from src.data_ingestion import DataIngestor
from src.feature_engineering import calculate_elo_ratings, create_feature_set
from src.training import train_pipeline
from src.backtesting import run_backtest
from src.predict import generate_prediction


def example_1_initialize_database():
    """Example: Initialize the database."""
    print("Example 1: Initializing database...")
    init_database()
    print("Database initialized!\n")


def example_2_fetch_data():
    """Example: Fetch historical data."""
    print("Example 2: Fetching historical data...")
    print("Note: This may take a while. Fetching data from 2020-2024...")
    
    ingestor = DataIngestor()
    # Fetch recent seasons (adjust as needed)
    ingestor.fetch_historical_games_and_stats(2020, 2024)
    ingestor.close()
    print("Data fetching complete!\n")


def example_3_calculate_elo():
    """Example: Calculate ELO ratings."""
    print("Example 3: Calculating ELO ratings...")
    
    db = get_session()
    try:
        calculate_elo_ratings(db)
        print("ELO ratings calculated!\n")
    finally:
        db.close()


def example_4_create_features():
    """Example: Create feature set."""
    print("Example 4: Creating feature set...")
    
    db = get_session()
    try:
        df = create_feature_set(db)
        print(f"Feature set created with {len(df)} rows")
        print(f"Columns: {df.columns.tolist()}\n")
    finally:
        db.close()


def example_5_train_model():
    """Example: Train the model."""
    print("Example 5: Training model...")
    print("Note: This may take several minutes...")
    
    train_pipeline()
    print("Model training complete!\n")


def example_6_backtest():
    """Example: Run backtesting."""
    print("Example 6: Running backtest...")
    
    results = run_backtest()
    if results:
        print(f"Backtest complete! ROI: {results['roi']:.2f}%\n")
    else:
        print("Backtest failed. Make sure you have odds data.\n")


def example_7_fetch_odds():
    """Example: Fetch historical odds from The Odds API."""
    print("Example 7: Fetching historical odds from The Odds API...")
    print("Note: This uses The Odds API which has rate limits.")
    
    from datetime import date
    ingestor = DataIngestor()
    try:
        # Fetch odds for a specific date range (e.g., last month)
        # Historical data available since mid-2020
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        ingestor.fetch_historical_odds_from_api(start_date, end_date)
        print("Historical odds fetched!\n")
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure your ODDS_API_KEY is configured.\n")
    finally:
        ingestor.close()


def example_8_predict():
    """Example: Make a prediction."""
    print("Example 8: Making a prediction...")
    
    db = get_session()
    try:
        # Example prediction
        result = generate_prediction(
            home_team_name="Lakers",
            away_team_name="Warriors",
            db=db
        )
        print(f"Prediction Result:")
        print(f"  {result['home_team']} vs {result['away_team']}")
        print(f"  Home Win Probability: {result['home_win_probability']:.2%}")
        print(f"  Away Win Probability: {result['away_win_probability']:.2%}")
        print(f"  Predicted Winner: {result['predicted_winner']}")
        print(f"  Confidence: {result['confidence']}\n")
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure you have data and a trained model.\n")
    finally:
        db.close()


def main():
    """Run all examples."""
    print("=" * 60)
    print("NBA Predictor - Example Usage")
    print("=" * 60)
    print()
    
    # Uncomment the examples you want to run:
    
    # example_1_initialize_database()
    # example_2_fetch_data()
    # example_3_calculate_elo()
    # example_4_create_features()
    # example_5_train_model()
    # example_6_backtest()
    # example_7_fetch_odds()
    # example_8_predict()
    
    print("Uncomment the examples you want to run in main() function.")


if __name__ == "__main__":
    main()

