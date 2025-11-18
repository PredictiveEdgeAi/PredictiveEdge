# PredictiveEdge - NBA Game Prediction System

A comprehensive machine learning system for predicting NBA game outcomes with a focus on profitability through value betting.

## Features

- **Data Ingestion**: Automated fetching of historical NBA data from basketball-reference
- **ELO Rating System**: Dynamic team strength ratings updated after each game
- **Advanced Feature Engineering**: Rolling averages, head-to-head records, rest days, and more
- **Multiple ML Models**: Logistic Regression, Random Forest, XGBoost, and LightGBM
- **Backtesting**: Profitability simulation with betting strategy evaluation
- **REST API**: FastAPI endpoints for live predictions
- **Daily Updates**: Automated data refresh and ELO recalculation

## Project Structure

```
PredictiveEdge/
├── backend/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI application
│   │   └── models.py        # Pydantic request/response models
│   ├── src/
│   │   ├── __init__.py
│   │   ├── config.py        # Configuration settings
│   │   ├── database.py      # Database schema and connection
│   │   ├── data_ingestion.py # Data fetching from APIs
│   │   ├── feature_engineering.py # ELO and feature creation
│   │   ├── training.py      # Model training pipeline
│   │   ├── backtesting.py   # Profitability simulation
│   │   └── predict.py       # Live prediction generation
│   ├── app.py              # Legacy FastAPI app (backward compatibility)
│   ├── model.py            # Legacy simple model
│   └── run_daily_update.py # Daily update automation script
├── frontend/               # Next.js frontend application
├── data/                   # Database and data files
├── model_artifacts/        # Saved models and scalers
├── notebooks/              # Jupyter notebooks for exploration
├── requirements.txt        # Python dependencies
└── .env                    # Environment variables
```

## Installation

1. **Clone the repository**:
```bash
git clone https://github.com/PredictiveEdgeAi/PredictiveEdge.git
cd PredictiveEdge
```

2. **Create a virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**:
Create a `.env` file in the root directory:
```env
ODDS_API_KEY="0738803dedc9c94e6b92206b67382f22"
DATABASE_URL="sqlite:///./data/nba_data.db"
```

**Note**: The API key is already configured in `src/config.py`, but you can override it in `.env` if needed. The Odds API free plan provides 500 requests per month, which is perfect for backtesting historical data.

## Usage

### 1. Initialize Database

```bash
cd backend
python -m src.database
```

### 2. Fetch Historical Data

```python
from src.data_ingestion import DataIngestor

ingestor = DataIngestor()
# Fetch data from 2010 to 2024
ingestor.fetch_historical_games_and_stats(2010, 2024)
ingestor.close()
```

### 3. Calculate ELO Ratings

```python
from src.database import get_session
from src.feature_engineering import calculate_elo_ratings

db = get_session()
calculate_elo_ratings(db)
db.close()
```

### 4. Fetch Historical Odds from The Odds API

The system is integrated with [The Odds API](https://the-odds-api.com/) to fetch historical and current odds data. The API provides historical data since mid-2020, perfect for backtesting.

**Option A: Using the dedicated script**:
```bash
cd backend
# Fetch odds for a date range (defaults to 2020-06-01 to today)
python fetch_historical_odds.py

# Or specify a date range
python fetch_historical_odds.py 2024-01-01 2024-01-31
```

**Option B: Using Python**:
```python
from src.data_ingestion import DataIngestor
from datetime import date

ingestor = DataIngestor()
# Fetch odds from The Odds API (historical data since mid-2020)
ingestor.fetch_historical_odds_from_api(
    start_date=date(2024, 1, 1),
    end_date=date(2024, 1, 31)
)
ingestor.close()
```

**Option C: Load from CSV (if you have your own data)**:
```python
from src.data_ingestion import DataIngestor

ingestor = DataIngestor()
ingestor.fetch_historical_odds("data/historical_odds.csv")
ingestor.close()
```

**Note**: The Odds API free plan allows 500 requests per month. The script includes rate limiting to stay within limits.

### 5. Train Models

```bash
cd backend
python -m src.training
```

This will:
- Calculate ELO ratings
- Create feature sets
- Split data temporally (train: 2010-2022, val: 2023, test: 2024)
- Train multiple models (Logistic Regression, Random Forest, XGBoost, LightGBM)
- Select the best model based on validation log loss
- Save the model and scaler to `model_artifacts/`

### 6. Run Backtesting

```bash
cd backend
python -m src.backtesting
```

This simulates betting strategy on the test set and calculates ROI.

### 7. Start the API Server

```bash
cd backend
python -m api.main
# Or using uvicorn directly:
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### 8. Make Predictions

**Using the API**:
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "home_team_name": "Lakers",
    "away_team_name": "Warriors",
    "home_moneyline": -150,
    "away_moneyline": +130
  }'
```

**Using Python**:
```python
from src.predict import generate_prediction
from src.database import get_session

db = get_session()
result = generate_prediction("Lakers", "Warriors", db=db)
print(result)
db.close()
```

### 9. Daily Updates

Set up a cron job or scheduled task to run daily updates:

```bash
cd backend
python run_daily_update.py
```

**Cron example** (runs daily at 2 AM):
```cron
0 2 * * * cd /path/to/PredictiveEdge/backend && python run_daily_update.py
```

## API Endpoints

### `GET /`
Health check endpoint.

### `GET /health`
Health check with status.

### `POST /predict`
Generate prediction for an upcoming game.

**Request Body**:
```json
{
  "home_team_name": "Lakers",
  "away_team_name": "Warriors",
  "game_date": "2024-01-15",  // Optional
  "home_moneyline": -150,      // Optional
  "away_moneyline": +130       // Optional
}
```

**Response**:
```json
{
  "home_team": "Los Angeles Lakers",
  "away_team": "Golden State Warriors",
  "home_win_probability": 0.65,
  "away_win_probability": 0.35,
  "confidence": "High",
  "predicted_winner": "Los Angeles Lakers",
  "value_bet_recommendation": "Bet Home (Los Angeles Lakers) - Edge: 5.2%"
}
```

### `POST /predict/legacy`
Legacy endpoint for backward compatibility with the original simple model.

## Feature Engineering

The system creates the following features for each game:

- **ELO Ratings**: Pre-game ELO for both teams and ELO difference
- **Rolling Averages** (last 10 games):
  - Points scored/allowed
  - Field goal percentage
  - Turnovers
  - Plus/minus
  - Rebounds
  - Assists
- **Head-to-Head**: Historical win percentage between teams
- **Rest Days**: Days since last game for both teams
- **Home Advantage**: Binary indicator

## Model Training

The training pipeline:
1. Uses **temporal splitting** (not random) to simulate real-world conditions
2. Trains multiple models and selects the best based on validation log loss
3. Uses early stopping to prevent overfitting
4. Saves the best model and scaler for production use

## Backtesting

The backtesting module:
- Simulates betting strategy on historical games
- Only places bets when model probability exceeds implied probability by a threshold (default 3%)
- Calculates ROI, win rate, and total profit/loss
- Saves detailed results to CSV

## Configuration

Key configuration options in `src/config.py`:

- `ELO_INITIAL`: Starting ELO rating (default: 1500)
- `ELO_K_FACTOR`: ELO update sensitivity (default: 20)
- `ELO_HOME_ADVANTAGE`: Home court advantage in ELO points (default: 100)
- `ROLLING_WINDOW`: Number of games for rolling averages (default: 10)
- `VALUE_EDGE_THRESHOLD`: Minimum edge for value betting (default: 0.03 = 3%)

## Notes

- The system requires historical data to be fetched before training
- ELO ratings must be calculated before creating feature sets
- The model must be trained before making predictions
- For production, replace `allow_origins=["*"]` in CORS with your frontend URL

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]
