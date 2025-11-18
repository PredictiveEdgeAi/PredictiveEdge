import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
ODDS_API_KEY = os.getenv("ODDS_API_KEY", "0738803dedc9c94e6b92206b67382f22")
ODDS_API_BASE_URL = "https://api.the-odds-api.com/v4"

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/nba_data.db")

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
MODEL_ARTIFACTS_DIR = PROJECT_ROOT / "model_artifacts"
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
MODEL_ARTIFACTS_DIR.mkdir(exist_ok=True)
NOTEBOOKS_DIR.mkdir(exist_ok=True)

# ELO Configuration
ELO_INITIAL = 1500
ELO_K_FACTOR = 20
ELO_HOME_ADVANTAGE = 100

# Model Configuration
ROLLING_WINDOW = 10  # Number of games for rolling averages
TRAIN_SEASONS = list(range(2010, 2023))  # 2010-2022
VAL_SEASON = 2023
TEST_SEASON = 2024

# Backtesting Configuration
VALUE_EDGE_THRESHOLD = 0.03  # 3% edge required to place a bet

