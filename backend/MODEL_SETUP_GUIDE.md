# Model Setup Guide

## Quick Setup (3 Steps)

### Step 1: Download Model from Kaggle
1. Go to your Kaggle notebook
2. Click on the **"Output"** tab in the right sidebar
3. Download `xgboost_nba_model.pkl`

### Step 2: Copy Model to Backend
**Option A: Using the setup script (Recommended)**
```bash
cd backend
python setup_model.py
# Enter the path to your downloaded model file when prompted
```

**Option B: Manual copy**
```bash
# Copy the downloaded file to:
model_artifacts/xgboost_nba_model.pkl
```

### Step 3: Test the API
```bash
# Start the API server
python -m api.main

# Or use the provided scripts:
# Windows: run_api.bat
# Mac/Linux: ./run_api.sh
```

## Verify Model is Loaded

Test the API endpoint:
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "home_team_name": "Lakers",
    "away_team_name": "Warriors"
  }'
```

## What Changed

✅ **Backend Updated:**
- `backend/src/predict.py` - Now loads XGBoost model (no scaler needed)
- Features updated to team1 vs team2 format (matches training)
- `is_home` feature removed (as in training)

✅ **Model Format:**
- Uses team strength features (ELO, recent form, H2H, rest days)
- No home/away bias - model learns from team strength
- Faster predictions (no feature scaling needed)

## Troubleshooting

**Error: "Model not found"**
- Make sure `xgboost_nba_model.pkl` is in `model_artifacts/` directory
- Check file name is exactly `xgboost_nba_model.pkl`

**Error: "Feature mismatch"**
- The model expects features in team1 vs team2 format
- All features are automatically created in `predict.py`
- No manual feature engineering needed

**Model file too large?**
- XGBoost models are typically 5-50 MB
- This is normal and expected

## Next Steps

Once the model is set up:
1. ✅ Backend is ready to serve predictions
2. ✅ Frontend can call `/predict` endpoint
3. ✅ No additional configuration needed

The API will automatically:
- Load the model on first prediction request
- Cache the model for faster subsequent requests
- Handle all feature engineering automatically

