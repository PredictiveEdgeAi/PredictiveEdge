# Quick Start Guide - How to Run NBA Predictor

## 🚀 Quick Start (5 Steps)

### Step 1: Navigate to Backend Directory
```powershell
cd PredictiveEdge\backend
```

### Step 2: Initialize Database
```powershell
python -m src.database
```
This creates the SQLite database and tables.

### Step 3: Start the API Server
```powershell
python -m api.main
```

Or using uvicorn:
```powershell
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 4: Test the API
Open your browser and go to:
- **Health Check**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### Step 5: Make a Prediction
Use the interactive docs at http://localhost:8000/docs or use curl:

```powershell
curl -X POST "http://localhost:8000/predict" -H "Content-Type: application/json" -d '{\"home_team_name\": \"Lakers\", \"away_team_name\": \"Warriors\"}'
```

---

## 📋 Full Setup (For Production Use)

### 1. Initialize Database
```powershell
cd PredictiveEdge\backend
python -m src.database
```

### 2. Fetch Historical Data (Optional - for training)
```powershell
python -c "from src.data_ingestion import DataIngestor; i = DataIngestor(); i.fetch_historical_games_and_stats(2020, 2024); i.close()"
```
**Note**: This takes time. Start with recent seasons (2020-2024) for testing.

### 3. Fetch Historical Odds (Optional - for backtesting)
```powershell
python fetch_historical_odds.py 2024-01-01 2024-01-31
```

### 4. Calculate ELO Ratings (Required before training)
```powershell
python -c "from src.database import get_session; from src.feature_engineering import calculate_elo_ratings; db = get_session(); calculate_elo_ratings(db); db.close()"
```

### 5. Train the Model (Required for predictions)
```powershell
python -m src.training
```
**Note**: This takes 10-30 minutes depending on data size.

### 6. Run Backtesting (Optional)
```powershell
python -m src.backtesting
```

### 7. Start the API Server
```powershell
python -m api.main
```

---

## 🎯 Common Commands

### Start API Server
```powershell
cd PredictiveEdge\backend
python -m api.main
```

### Check if API is Running
Open browser: http://localhost:8000

### View API Documentation
Open browser: http://localhost:8000/docs

### Test Prediction (PowerShell)
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/predict" -Method POST -ContentType "application/json" -Body '{"home_team_name": "Lakers", "away_team_name": "Warriors"}'
```

---

## ⚠️ Troubleshooting

### "Model not found" Error
You need to train the model first:
```powershell
python -m src.training
```

### "Database not found" Error
Initialize the database:
```powershell
python -m src.database
```

### "No module named 'src'" Error
Make sure you're in the `backend` directory:
```powershell
cd PredictiveEdge\backend
```

### Port Already in Use
Change the port:
```powershell
uvicorn api.main:app --reload --port 8001
```

---

## 📝 Notes

- **For Quick Testing**: You can use the legacy endpoint at `/predict/legacy` which uses a simple model (no training needed)
- **For Production**: You need to train the model first (Step 5 in Full Setup)
- **API Key**: Already configured in `src/config.py` - no need to set up `.env` unless you want to override it

---

## 🎮 Next Steps

1. **Test the API**: Visit http://localhost:8000/docs
2. **Train the Model**: Run `python -m src.training` (requires data)
3. **Fetch Data**: Use `DataIngestor` to get historical NBA data
4. **Integrate Frontend**: The frontend is in the `frontend/` directory

