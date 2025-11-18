"""
Pydantic models for API requests and responses.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class PredictionRequest(BaseModel):
    """Request model for game prediction."""
    home_team_name: str = Field(..., description="Name or abbreviation of home team")
    away_team_name: str = Field(..., description="Name or abbreviation of away team")
    game_date: Optional[date] = Field(None, description="Date of the game (defaults to today)")
    home_moneyline: Optional[int] = Field(None, description="Home team moneyline odds (optional)")
    away_moneyline: Optional[int] = Field(None, description="Away team moneyline odds (optional)")


class PredictionResponse(BaseModel):
    """Response model for game prediction."""
    home_team: str
    away_team: str
    home_win_probability: float = Field(..., ge=0.0, le=1.0, description="Probability of home team winning")
    away_win_probability: float = Field(..., ge=0.0, le=1.0, description="Probability of away team winning")
    confidence: str = Field(..., description="Confidence level: High, Medium, or Low")
    predicted_winner: str = Field(..., description="Predicted winner")
    value_bet_recommendation: Optional[str] = Field(None, description="Betting recommendation if odds provided")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    message: str

