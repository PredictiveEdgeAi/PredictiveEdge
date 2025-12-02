"""
Prediction module for NBA Predictor.
Generates predictions for upcoming games.
"""
import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from sqlalchemy.orm import Session
from src.database import get_session, Team, Game
from src.config import MODEL_ARTIFACTS_DIR
from src.feature_engineering import (
    get_rolling_averages, get_h2h_win_pct, get_days_rest,
    ELO_INITIAL
)
# Note: We no longer use FEATURE_COLUMNS from training.py
# The new XGBoost model uses team1 vs team2 feature format
from datetime import datetime, date

# Global model cache (loaded once, reused for all predictions)
_model_cache = None


def load_model():
    """Load the saved XGBoost model (no scaler needed). Uses caching for performance."""
    global _model_cache
    
    # Return cached model if available
    if _model_cache is not None:
        return _model_cache, None
    
    # Try new XGBoost model first
    model_path = MODEL_ARTIFACTS_DIR / "xgboost_nba_model.pkl"
    
    # Fallback to old model if new one doesn't exist
    if not model_path.exists():
        model_path = MODEL_ARTIFACTS_DIR / "best_model.joblib"
    
    if not model_path.exists():
        raise FileNotFoundError(
            f"Model not found. Please place 'xgboost_nba_model.pkl' in {MODEL_ARTIFACTS_DIR}. "
            f"Download it from Kaggle notebook output. See backend/MODEL_SETUP_GUIDE.md for instructions."
        )
    
    print(f"Loading model from {model_path}...")
    model = joblib.load(model_path)
    
    # Cache the model for future use
    _model_cache = model
    
    # XGBoost models don't need a scaler
    return model, None


def get_team_by_name(db: Session, team_name: str) -> Team:
    """
    Get team by name or abbreviation.
    Tries exact match first, then abbreviation match.
    """
    # Try exact name match
    team = db.query(Team).filter_by(team_name=team_name).first()
    if team:
        return team
    
    # Try abbreviation match
    team = db.query(Team).filter_by(abbreviation=team_name.upper()).first()
    if team:
        return team
    
    raise ValueError(f"Team '{team_name}' not found in database.")


def get_current_elo(db: Session, team_id: int) -> float:
    """
    Get the current ELO rating for a team (from most recent game).
    """
    # Get the most recent game for this team
    recent_game = db.query(Game).filter(
        (Game.home_team_id == team_id) | (Game.away_team_id == team_id),
        Game.home_team_pregame_elo.isnot(None)
    ).order_by(Game.date.desc()).first()
    
    if not recent_game:
        return ELO_INITIAL
    
    # Return the ELO from the most recent game (post-game ELO would be higher)
    # We'll use pre-game ELO and update it based on the result
    if recent_game.home_team_id == team_id:
        elo = recent_game.home_team_pregame_elo
    else:
        elo = recent_game.away_team_pregame_elo
    
    # If the team won, add some ELO points (approximate)
    if recent_game.home_score is not None and recent_game.away_score is not None:
        if (recent_game.home_team_id == team_id and recent_game.home_score > recent_game.away_score) or \
           (recent_game.away_team_id == team_id and recent_game.away_score > recent_game.home_score):
            # Team won, add approximate ELO gain
            elo += 15  # Approximate gain
        else:
            # Team lost, subtract approximate ELO loss
            elo -= 15  # Approximate loss
    
    return elo


def generate_prediction(
    home_team_name: str,
    away_team_name: str,
    game_date: date = None,
    db: Session = None
) -> dict:
    """
    Generate prediction for an upcoming game.
    
    Args:
        home_team_name: Name or abbreviation of home team
        away_team_name: Name or abbreviation of away team
        game_date: Date of the game (defaults to today)
        db: Database session (if None, creates new one)
    
    Returns:
        Dictionary with prediction results
    """
    if db is None:
        db = get_session()
        close_db = True
    else:
        close_db = False
    
    try:
        if game_date is None:
            game_date = datetime.now().date()
        
        # Load model (XGBoost doesn't need scaler)
        model, _ = load_model()
        
        # Get teams
        home_team = get_team_by_name(db, home_team_name)
        away_team = get_team_by_name(db, away_team_name)
        
        # Get current ELO ratings
        home_elo = get_current_elo(db, home_team.team_id)
        away_elo = get_current_elo(db, away_team.team_id)
        
        # Get rolling averages
        home_rolling = get_rolling_averages(db, home_team.team_id, game_date)
        away_rolling = get_rolling_averages(db, away_team.team_id, game_date)
        
        # Get H2H
        h2h_home = get_h2h_win_pct(db, home_team.team_id, away_team.team_id, game_date)
        h2h_away = get_h2h_win_pct(db, away_team.team_id, home_team.team_id, game_date)
        
        # Get rest days
        home_rest = get_days_rest(db, home_team.team_id, game_date)
        away_rest = get_days_rest(db, away_team.team_id, game_date)
        
        # Calculate offensive/defensive ratings (using rolling averages)
        home_offensive_rating = home_rolling.get('avg_pts_scored', 0)
        home_defensive_rating = home_rolling.get('avg_pts_allowed', 0)
        away_offensive_rating = away_rolling.get('avg_pts_scored', 0)
        away_defensive_rating = away_rolling.get('avg_pts_allowed', 0)
        
        # Create feature vector in team1 vs team2 format (team1 = home, team2 = away)
        # This matches the format used in training (is_home was removed)
        features = {
            # Team strength
            'team1_elo': home_elo,
            'team2_elo': away_elo,
            'elo_diff': home_elo - away_elo,
            
            # Offensive/Defensive ratings
            'team1_offensive_rating': home_offensive_rating,
            'team1_defensive_rating': home_defensive_rating,
            'team2_offensive_rating': away_offensive_rating,
            'team2_defensive_rating': away_defensive_rating,
            
            # Recent form (rolling averages) - Team1 (home)
            'team1_avg_pts_scored_l10': home_rolling.get('avg_pts_scored', 0),
            'team1_avg_pts_allowed_l10': home_rolling.get('avg_pts_allowed', 0),
            'team1_avg_fg_pct_l10': home_rolling.get('avg_fg_pct', 0),
            'team1_avg_rebounds_l10': home_rolling.get('avg_rebounds', 0),
            'team1_avg_assists_l10': home_rolling.get('avg_assists', 0),
            'team1_avg_tov_l10': home_rolling.get('avg_tov', 0),
            'team1_avg_plus_minus_l10': home_rolling.get('avg_plus_minus', 0),
            
            # Recent form (rolling averages) - Team2 (away)
            'team2_avg_pts_scored_l10': away_rolling.get('avg_pts_scored', 0),
            'team2_avg_pts_allowed_l10': away_rolling.get('avg_pts_allowed', 0),
            'team2_avg_fg_pct_l10': away_rolling.get('avg_fg_pct', 0),
            'team2_avg_rebounds_l10': away_rolling.get('avg_rebounds', 0),
            'team2_avg_assists_l10': away_rolling.get('avg_assists', 0),
            'team2_avg_tov_l10': away_rolling.get('avg_tov', 0),
            'team2_avg_plus_minus_l10': away_rolling.get('avg_plus_minus', 0),
            
            # Head-to-head
            'team1_h2h_win_pct': h2h_home,
            'team2_h2h_win_pct': h2h_away,
            
            # Rest days
            'team1_rest_days': home_rest,
            'team2_rest_days': away_rest,
            'rest_advantage': home_rest - away_rest,
            
            # Strength differentials
            'offensive_rating_diff': home_offensive_rating - away_offensive_rating,
            'defensive_rating_diff': away_defensive_rating - home_defensive_rating,  # Lower is better for defense
            'pts_scored_diff_l10': home_rolling.get('avg_pts_scored', 0) - away_rolling.get('avg_pts_scored', 0),
            'pts_allowed_diff_l10': away_rolling.get('avg_pts_allowed', 0) - home_rolling.get('avg_pts_allowed', 0),
            'plus_minus_diff_l10': home_rolling.get('avg_plus_minus', 0) - away_rolling.get('avg_plus_minus', 0),
        }
        
        # Note: Interaction features (off_vs_def_matchup, scoring_vs_defense) were not included
        # in the final model training, so we don't include them here to match the 31 expected features
        
        # Get model's expected feature order (if available)
        if hasattr(model, 'feature_names_in_'):
            feature_order = list(model.feature_names_in_)
        else:
            # Fallback: use the features we created (model will handle ordering)
            feature_order = list(features.keys())
        
        # Create feature array in correct order
        feature_vector = np.array([[features.get(col, 0) for col in feature_order]])
        
        # Get prediction (XGBoost doesn't need scaling)
        probabilities = model.predict_proba(feature_vector)[0]
        # Model predicts team1_won (1 = team1 wins, 0 = team2 wins)
        # Since team1 = home, probabilities[1] = home win prob
        home_win_prob = probabilities[1] if len(probabilities) > 1 else probabilities[0]
        away_win_prob = probabilities[0] if len(probabilities) > 1 else (1 - probabilities[0])
        
        # Determine confidence
        if abs(home_win_prob - 0.5) > 0.2:
            confidence = "High"
        elif abs(home_win_prob - 0.5) > 0.1:
            confidence = "Medium"
        else:
            confidence = "Low"
        
        return {
            'home_team': home_team.team_name,
            'away_team': away_team.team_name,
            'home_win_probability': float(home_win_prob),
            'away_win_probability': float(away_win_prob),
            'confidence': confidence,
            'predicted_winner': home_team.team_name if home_win_prob > 0.5 else away_team.team_name,
            'features': features  # For debugging
        }
        
    finally:
        if close_db:
            db.close()


def generate_prediction_with_value(
    home_team_name: str,
    away_team_name: str,
    home_moneyline: int = None,
    away_moneyline: int = None,
    game_date: date = None,
    db: Session = None
) -> dict:
    """
    Generate prediction with value bet recommendation.
    
    Args:
        home_team_name: Name or abbreviation of home team
        away_team_name: Name or abbreviation of away team
        home_moneyline: Home team moneyline odds (optional)
        away_moneyline: Away team moneyline odds (optional)
        game_date: Date of the game
        db: Database session
    
    Returns:
        Dictionary with prediction and value bet recommendation
    """
    from src.backtesting import moneyline_to_implied_prob, VALUE_EDGE_THRESHOLD
    
    prediction = generate_prediction(home_team_name, away_team_name, game_date, db)
    
    value_recommendation = "No Value"
    
    if home_moneyline is not None and away_moneyline is not None:
        home_implied_prob = moneyline_to_implied_prob(home_moneyline)
        away_implied_prob = moneyline_to_implied_prob(away_moneyline)
        
        home_edge = prediction['home_win_probability'] - home_implied_prob
        away_edge = prediction['away_win_probability'] - away_implied_prob
        
        if home_edge > VALUE_EDGE_THRESHOLD:
            value_recommendation = f"Bet Home ({home_team_name}) - Edge: {home_edge*100:.1f}%"
        elif away_edge > VALUE_EDGE_THRESHOLD:
            value_recommendation = f"Bet Away ({away_team_name}) - Edge: {away_edge*100:.1f}%"
    
    prediction['value_bet_recommendation'] = value_recommendation
    
    return prediction


if __name__ == "__main__":
    # Example usage
    db = get_session()
    try:
        result = generate_prediction("Lakers", "Warriors")
        print(result)
    finally:
        db.close()

