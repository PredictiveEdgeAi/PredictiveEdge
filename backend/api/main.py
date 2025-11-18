"""
FastAPI main application for NBA Predictor API.
"""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.models import PredictionRequest, PredictionResponse, HealthResponse
from src.predict import generate_prediction, generate_prediction_with_value
from src.database import get_db_connection, init_database

app = FastAPI(
    title="NBA Prediction API",
    description="AI-driven predictions for NBA games with ELO ratings and advanced features",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_database()


@app.get("/", response_model=HealthResponse)
def root():
    """Root endpoint."""
    return HealthResponse(
        status="ok",
        message="NBA Prediction API is running successfully 🏀"
    )


@app.get("/health", response_model=HealthResponse)
def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="ok",
        message="API is healthy"
    )


@app.post("/predict", response_model=PredictionResponse)
async def predict_game(
    request: PredictionRequest,
    db: Session = Depends(get_db_connection)
):
    """
    Predict the outcome of an NBA game.
    
    Takes home team and away team names and returns win probabilities,
    confidence level, and value bet recommendation (if odds provided).
    """
    try:
        # Generate prediction
        if request.home_moneyline is not None and request.away_moneyline is not None:
            result = generate_prediction_with_value(
                home_team_name=request.home_team_name,
                away_team_name=request.away_team_name,
                home_moneyline=request.home_moneyline,
                away_moneyline=request.away_moneyline,
                game_date=request.game_date,
                db=db
            )
        else:
            result = generate_prediction(
                home_team_name=request.home_team_name,
                away_team_name=request.away_team_name,
                game_date=request.game_date,
                db=db
            )
            result['value_bet_recommendation'] = None
        
        return PredictionResponse(**result)
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=503,
            detail="Model not found. Please train the model first."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# Legacy endpoint for backward compatibility
@app.post("/predict/legacy")
def predict_legacy(data: dict):
    """
    Legacy prediction endpoint for backward compatibility.
    Uses simple model with basic statistics.
    """
    try:
        from model import predict_outcome
        
        features = [
            data.get('teamPointsPerGame', 0),
            data.get('opponentPointsPerGame', 0),
            data.get('fieldGoalPercentage', 0),
            data.get('threePointPercentage', 0),
            data.get('reboundsPerGame', 0),
            data.get('assistsPerGame', 0)
        ]
        prediction = predict_outcome(features)
        return {"prediction": str(prediction)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

