from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.predict import generate_prediction

app = FastAPI(title="PredictiveEdge Basketball API")

# ✅ Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # you can replace "*" with "http://localhost:3000" later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class InputData(BaseModel):
    home_team_name: str
    away_team_name: str

@app.get("/")
def home():
    return {"message": "PredictiveEdge Basketball API is running successfully 🏀"}

@app.get("/teams")
def get_teams():
    """Get all teams from the database."""
    from src.database import get_session, Team
    
    db = get_session()
    try:
        teams = db.query(Team).order_by(Team.team_name).all()
        return {
            "teams": [
                {
                    "id": team.abbreviation.lower(),
                    "name": team.team_name.split()[-1] if len(team.team_name.split()) > 1 else team.team_name,
                    "city": " ".join(team.team_name.split()[:-1]) if len(team.team_name.split()) > 1 else "",
                    "abbreviation": team.abbreviation,
                    "fullName": team.team_name
                }
                for team in teams
            ]
        }
    finally:
        db.close()

@app.post("/predict")
def predict(data: InputData):
    """
    Predict game outcome using the XGBoost model.
    
    Returns:
        - prediction: "1" if home team wins, "0" if home team loses
    """
    try:
        # Use the real XGBoost model to generate prediction
        result = generate_prediction(
            home_team_name=data.home_team_name,
            away_team_name=data.away_team_name
        )
        
        # Extract prediction: 1 if home team wins (probability > 0.5), 0 otherwise
        home_win_prob = result.get('home_win_probability', 0.5)
        away_win_prob = result.get('away_win_probability', 0.5)
        prediction = "1" if home_win_prob > 0.5 else "0"
        
        # Convert probabilities to percentages
        home_win_percentage = round(home_win_prob * 100, 2)
        away_win_percentage = round(away_win_prob * 100, 2)
        
        return {
            "prediction": prediction,
            "home_win_probability": home_win_percentage,
            "away_win_probability": away_win_percentage
        }
        
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Model not found: {str(e)}"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=f"Team not found: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction error: {str(e)}"
        )
