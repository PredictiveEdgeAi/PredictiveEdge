"""
Quick start script to set up and run the NBA Predictor system.
This script automates the initial setup process.
"""
import os
import sys
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed."""
    required_packages = [
        'pandas', 'numpy', 'sklearn', 'xgboost', 'lightgbm',
        'fastapi', 'uvicorn', 'sqlalchemy', 'requests'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"Missing packages: {', '.join(missing)}")
        print("Please run: pip install -r requirements.txt")
        return False
    return True


def setup_directories():
    """Create necessary directories."""
    dirs = ['data', 'model_artifacts', 'notebooks']
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
    print("✓ Directories created")


def initialize_database():
    """Initialize the database."""
    try:
        from src.database import init_database
        init_database()
        print("✓ Database initialized")
        return True
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        return False


def main():
    """Main quick start function."""
    print("=" * 60)
    print("NBA Predictor - Quick Start")
    print("=" * 60)
    print()
    
    # Check dependencies
    print("Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    print("✓ All dependencies installed")
    print()
    
    # Setup directories
    print("Setting up directories...")
    setup_directories()
    print()
    
    # Initialize database
    print("Initializing database...")
    if not initialize_database():
        sys.exit(1)
    print()
    
    print("=" * 60)
    print("Quick start complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Fetch historical data:")
    print("   python -c \"from src.data_ingestion import DataIngestor; i = DataIngestor(); i.fetch_historical_games_and_stats(2020, 2024); i.close()\"")
    print()
    print("2. Calculate ELO ratings:")
    print("   python -c \"from src.database import get_session; from src.feature_engineering import calculate_elo_ratings; db = get_session(); calculate_elo_ratings(db); db.close()\"")
    print()
    print("3. Train the model:")
    print("   python -m src.training")
    print()
    print("4. Start the API:")
    print("   python -m api.main")
    print()
    print("For detailed instructions, see SETUP.md")


if __name__ == "__main__":
    main()

