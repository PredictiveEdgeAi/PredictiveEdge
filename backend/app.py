from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import model

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
    teamPointsPerGame: float
    opponentPointsPerGame: float
    fieldGoalPercentage: float
    threePointPercentage: float
    reboundsPerGame: float
    assistsPerGame: float

@app.get("/")
def home():
    return {"message": "PredictiveEdge Basketball API is running successfully 🏀"}

@app.post("/predict")
def predict(data: InputData):
    features = [
        data.teamPointsPerGame,
        data.opponentPointsPerGame,
        data.fieldGoalPercentage,
        data.threePointPercentage,
        data.reboundsPerGame,
        data.assistsPerGame
    ]
    prediction = model.predict_outcome(features)
    return {"prediction": str(prediction)}
