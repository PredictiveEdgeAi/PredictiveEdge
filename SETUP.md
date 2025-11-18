# Setup Guide

This guide will walk you through setting up the NBA Predictor system from scratch.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git (for cloning the repository)

## Step-by-Step Setup

### 1. Clone and Navigate

```bash
git clone https://github.com/PredictiveEdgeAi/PredictiveEdge.git
cd PredictiveEdge
```

### 2. Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Create a `.env` file in the root directory:

```env
ODDS_API_KEY="your_api_key_here"
DATABASE_URL="sqlite:///./data/nba_data.db"
```

**Note:** The Odds API key is optional. You can get one from [The Odds API](https://the-odds-api.com/), but the system will work without it (you just won't be able to fetch live odds).

### 5. Initialize Database

```bash
cd backend
python -m src.database
```

This creates the SQLite database and all necessary tables.

### 6. Fetch Historical Data

**Option A: Using Python Script**

```python
from src.data_ingestion import DataIngestor

ingestor = DataIngestor()
# Fetch data from 2010 to 2024 (this will take a while!)
ingestor.fetch_historical_games_and_stats(2010, 2024)
ingestor.close()
```

**Option B: Using Command Line**

```bash
cd backend
python -c "from src.data_ingestion import DataIngestor; i = DataIngestor(); i.fetch_historical_games_and_stats(2020, 2024); i.close()"
```

**Note:** Fetching data can take a long time (hours for many seasons). Start with recent seasons (e.g., 2020-2024) for testing.

### 7. Load Historical Odds (Optional)

If you have historical odds data in CSV format, place it in `data/historical_odds.csv` and run:

```python
from src.data_ingestion import DataIngestor

ingestor = DataIngestor()
ingestor.fetch_historical_odds("data/historical_odds.csv")
ingestor.close()
```

See `data/historical_odds.csv.example` for the expected format.

### 8. Calculate ELO Ratings

```bash
cd backend
python -c "from src.database import get_session; from src.feature_engineering import calculate_elo_ratings; db = get_session(); calculate_elo_ratings(db); db.close()"
```

### 9. Train the Model

```bash
cd backend
python -m src.training
```

This will:
- Create feature sets
- Split data temporally
- Train multiple models
- Select the best model
- Save it to `model_artifacts/`

**Note:** Training can take 10-30 minutes depending on your data size and hardware.

### 10. (Optional) Run Backtesting

```bash
cd backend
python -m src.backtesting
```

This simulates betting on the test set and shows profitability metrics.

### 11. Start the API Server

```bash
cd backend
python -m api.main
```

Or using uvicorn directly:

```bash
cd backend
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### 12. Test the API

Open your browser and visit:
- `http://localhost:8000` - Health check
- `http://localhost:8000/docs` - Interactive API documentation

Or use curl:

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "home_team_name": "Lakers",
    "away_team_name": "Warriors"
  }'
```

## Troubleshooting

### Import Errors

If you get import errors, make sure you're running commands from the `backend` directory or have the correct Python path set.

### Database Errors

If you get database errors, make sure you've initialized the database (Step 5) and that the `data/` directory exists.

### Model Not Found

If you get "Model not found" errors, make sure you've trained the model (Step 9).

### Data Fetching Issues

The basketball-reference scraper may have rate limits. If you encounter errors:
- Add delays between requests
- Fetch data in smaller batches
- Check your internet connection

### Team Name Not Found

Team names must match exactly as they appear in the database. You can check available teams:

```python
from src.database import get_session, Team

db = get_session()
teams = db.query(Team).all()
for team in teams:
    print(f"{team.team_name} ({team.abbreviation})")
db.close()
```

## Next Steps

- Set up daily updates using cron (see `run_daily_update.py`)
- Integrate with your frontend
- Fine-tune model hyperparameters
- Add more features
- Experiment with different models

## Support

For issues or questions, please open an issue on GitHub.

