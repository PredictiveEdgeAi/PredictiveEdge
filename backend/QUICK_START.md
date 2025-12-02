# Quick Start Guide - API Testing

## ✅ Setup Complete!

1. ✅ Teams populated in database (30 NBA teams)
2. ✅ Model file ready (`model_artifacts/xgboost_nba_model.pkl`)
3. ✅ Test scripts created

## 🚀 How to Test the API

### Step 1: Start the API Server

Open a PowerShell terminal and run:
```powershell
cd backend
python -m api.main
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### Step 2: Test the API (in a NEW terminal)

Keep the server running, open a **new** PowerShell window:

```powershell
cd backend
.\test_api_complete.ps1
```

## 📋 Available Scripts

### `populate_teams.py`
Populates the database with all 30 NBA teams.
```powershell
python populate_teams.py
```

### `test_api_complete.ps1`
Complete API test script that:
- Checks teams in database
- Tests health endpoint
- Makes a prediction
- Shows formatted results

```powershell
.\test_api_complete.ps1
```

## 🧪 Manual Testing

### Test 1: Health Check
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/health" | Select-Object -ExpandProperty Content
```

### Test 2: Make Prediction
```powershell
$body = @{
    home_team_name = "Los Angeles Lakers"
    away_team_name = "Golden State Warriors"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/predict" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body | Select-Object -ExpandProperty Content
```

### Test 3: With Betting Odds
```powershell
$body = @{
    home_team_name = "Los Angeles Lakers"
    away_team_name = "Golden State Warriors"
    home_moneyline = -150
    away_moneyline = 130
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/predict" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body | Select-Object -ExpandProperty Content
```

## 📝 Team Names

You can use either:
- **Full names**: "Los Angeles Lakers", "Golden State Warriors"
- **Abbreviations**: "LAL", "GSW"

All 30 NBA teams are available:
- Lakers (LAL), Warriors (GSW), Celtics (BOS), Heat (MIA), Bulls (CHI)
- Knicks (NYK), 76ers (PHI), Nets (BKN), Bucks (MIL), Raptors (TOR)
- Pacers (IND), Cavaliers (CLE), Pistons (DET), Magic (ORL), Hornets (CHA)
- Wizards (WAS), Hawks (ATL), Mavericks (DAL), Rockets (HOU), Spurs (SAS)
- Grizzlies (MEM), Pelicans (NOP), Thunder (OKC), Nuggets (DEN), Jazz (UTA)
- Trail Blazers (POR), Timberwolves (MIN), Kings (SAC), Suns (PHX), Clippers (LAC)

## 🎯 Expected Response

```json
{
  "home_team": "Los Angeles Lakers",
  "away_team": "Golden State Warriors",
  "home_win_probability": 0.65,
  "away_win_probability": 0.35,
  "confidence": "High",
  "predicted_winner": "Los Angeles Lakers",
  "value_bet_recommendation": null
}
```

## ⚠️ Troubleshooting

**"Team not found"**
- Run: `python populate_teams.py`

**"Model not found"**
- Make sure `xgboost_nba_model.pkl` is in `model_artifacts/` folder
- Download from Kaggle notebook output if missing

**"API not accessible"**
- Make sure API server is running: `python -m api.main`
- Check if port 8000 is available

## ✅ Ready for Frontend!

Once the API is working, your friend can use it from the frontend:
- Endpoint: `http://localhost:8000/predict`
- Method: `POST`
- Content-Type: `application/json`

The API is production-ready! 🚀

