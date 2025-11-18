"""
Daily update script for NBA Predictor.
Should be run via cron job or scheduled task.
"""
from src.data_ingestion import DataIngestor
from src.feature_engineering import calculate_elo_ratings
from src.database import get_session
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('daily_update.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def run_daily_update():
    """Run daily data update and ELO recalculation."""
    logger.info("=" * 60)
    logger.info("Starting daily update process")
    logger.info("=" * 60)
    
    try:
        # Step 1: Update data
        logger.info("[Step 1/2] Updating daily data...")
        ingestor = DataIngestor()
        ingestor.update_daily_data()
        ingestor.close()
        logger.info("Daily data update complete.")
        
        # Step 2: Recalculate ELO ratings
        logger.info("[Step 2/2] Recalculating ELO ratings...")
        db = get_session()
        try:
            calculate_elo_ratings(db)
            logger.info("ELO ratings updated.")
        finally:
            db.close()
        
        logger.info("=" * 60)
        logger.info("Daily update process completed successfully!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Error during daily update: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    run_daily_update()

