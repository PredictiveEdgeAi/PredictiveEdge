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
from src.config import MODEL_ARTIFACTS_DIR, DATA_DIR
from src.feature_engineering import (
    get_rolling_averages, get_h2h_win_pct, get_days_rest,
    ELO_INITIAL
)
# Note: We no longer use FEATURE_COLUMNS from training.py
# The new XGBoost model uses team1 vs team2 feature format
from datetime import datetime, date

# Global model cache (loaded once, reused for all predictions)
_model_cache = None
_training_data_cache = None


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


def load_training_data():
    """Load the training dataset CSV. Uses caching for performance."""
    global _training_data_cache
    
    if _training_data_cache is not None:
        return _training_data_cache
    
    training_data_path = DATA_DIR / "training_dataset_engineered.csv"
    
    if not training_data_path.exists():
        raise FileNotFoundError(
            f"Training dataset not found at {training_data_path}. "
            f"Please ensure training_dataset_engineered.csv is in the data folder."
        )
    
    print(f"Loading training dataset from {training_data_path}...")
    df = pd.read_csv(training_data_path, parse_dates=['game_date'])
    
    # Cache the dataset
    _training_data_cache = df
    
    return df


def get_team_stats_from_training_data(team_name: str, training_df: pd.DataFrame, game_date: date = None):
    """
    Get the most recent team statistics from the training dataset.
    
    Args:
        team_name: Name of the team
        training_df: The training dataset DataFrame
        game_date: Date to get stats before (defaults to today)
    
    Returns:
        Dictionary with team statistics or None if not found
    """
    if game_date is None:
        game_date = datetime.now().date()
    
    # Find most recent game where this team was team1 (with actual data)
    team1_games = training_df[
        (training_df['team1_name'] == team_name) &
        (training_df['game_date'] < pd.Timestamp(game_date)) &
        (training_df['team1_avg_pts_scored_l10'] > 0)  # Has actual data
    ].sort_values('game_date', ascending=False)
    
    if len(team1_games) > 0:
        latest_game = team1_games.iloc[0]
        return {
            'elo': float(latest_game['team1_elo']),
            'offensive_rating': float(latest_game['team1_offensive_rating']),
            'defensive_rating': float(latest_game['team1_defensive_rating']),
            'avg_pts_scored_l10': float(latest_game['team1_avg_pts_scored_l10']),
            'avg_pts_allowed_l10': float(latest_game['team1_avg_pts_allowed_l10']),
            'avg_fg_pct_l10': float(latest_game['team1_avg_fg_pct_l10']),
            'avg_rebounds_l10': float(latest_game['team1_avg_rebounds_l10']),
            'avg_assists_l10': float(latest_game['team1_avg_assists_l10']),
            'avg_tov_l10': float(latest_game['team1_avg_tov_l10']),
            'avg_plus_minus_l10': float(latest_game['team1_avg_plus_minus_l10']),
        }
    
    # Try team2
    team2_games = training_df[
        (training_df['team2_name'] == team_name) &
        (training_df['game_date'] < pd.Timestamp(game_date)) &
        (training_df['team2_avg_pts_scored_l10'] > 0)  # Has actual data
    ].sort_values('game_date', ascending=False)
    
    if len(team2_games) > 0:
        latest_game = team2_games.iloc[0]
        return {
            'elo': float(latest_game['team2_elo']),
            'offensive_rating': float(latest_game['team2_offensive_rating']),
            'defensive_rating': float(latest_game['team2_defensive_rating']),
            'avg_pts_scored_l10': float(latest_game['team2_avg_pts_scored_l10']),
            'avg_pts_allowed_l10': float(latest_game['team2_avg_pts_allowed_l10']),
            'avg_fg_pct_l10': float(latest_game['team2_avg_fg_pct_l10']),
            'avg_rebounds_l10': float(latest_game['team2_avg_rebounds_l10']),
            'avg_assists_l10': float(latest_game['team2_avg_assists_l10']),
            'avg_tov_l10': float(latest_game['team2_avg_tov_l10']),
            'avg_plus_minus_l10': float(latest_game['team2_avg_plus_minus_l10']),
        }
    
    return None


def get_h2h_from_training_data(team1_name: str, team2_name: str, training_df: pd.DataFrame, game_date: date = None):
    """
    Get head-to-head win percentage from training data.
    
    Args:
        team1_name: Name of team 1
        team2_name: Name of team 2
        training_df: The training dataset DataFrame
        game_date: Date to get stats before (defaults to today)
    
    Returns:
        Tuple of (team1_h2h_win_pct, team2_h2h_win_pct)
    """
    if game_date is None:
        game_date = datetime.now().date()
    
    # Find games between these two teams before the game date
    h2h_games = training_df[
        (
            ((training_df['team1_name'] == team1_name) & (training_df['team2_name'] == team2_name)) |
            ((training_df['team1_name'] == team2_name) & (training_df['team2_name'] == team1_name))
        ) &
        (training_df['game_date'] < pd.Timestamp(game_date)) &
        (training_df['team1_score'].notna()) &
        (training_df['team2_score'].notna())
    ]
    
    if len(h2h_games) == 0:
        return 0.5, 0.5  # Default to 50% if no history
    
    team1_wins = 0
    for _, game in h2h_games.iterrows():
        if game['team1_name'] == team1_name:
            if game['team1_won'] == 1:
                team1_wins += 1
        else:  # team1_name == team2_name
            if game['team1_won'] == 0:  # team2 won (as team1)
                team1_wins += 1
    
    team1_h2h = team1_wins / len(h2h_games) if len(h2h_games) > 0 else 0.5
    team2_h2h = 1 - team1_h2h
    
    return team1_h2h, team2_h2h


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
        
        # Load training dataset for historical data
        training_df = load_training_data()
        
        # Get teams from database (for team_id if needed)
        try:
            home_team = get_team_by_name(db, home_team_name)
            away_team = get_team_by_name(db, away_team_name)
        except ValueError:
            # If team not in database, use the name directly
            home_team = type('Team', (), {'team_id': None, 'team_name': home_team_name})()
            away_team = type('Team', (), {'team_id': None, 'team_name': away_team_name})()
        
        # Get team statistics from training dataset
        home_stats = get_team_stats_from_training_data(home_team_name, training_df, game_date)
        away_stats = get_team_stats_from_training_data(away_team_name, training_df, game_date)
        
        # Use training data if available, otherwise fall back to database/defaults
        if home_stats:
            home_elo = home_stats['elo']
            home_offensive_rating = home_stats['offensive_rating']
            home_defensive_rating = home_stats['defensive_rating']
            home_rolling = {
                'avg_pts_scored': home_stats['avg_pts_scored_l10'],
                'avg_pts_allowed': home_stats['avg_pts_allowed_l10'],
                'avg_fg_pct': home_stats['avg_fg_pct_l10'],
                'avg_rebounds': home_stats['avg_rebounds_l10'],
                'avg_assists': home_stats['avg_assists_l10'],
                'avg_tov': home_stats['avg_tov_l10'],
                'avg_plus_minus': home_stats['avg_plus_minus_l10'],
            }
        else:
            # Fallback to database/defaults
            if home_team.team_id:
                home_elo = get_current_elo(db, home_team.team_id)
                home_rolling = get_rolling_averages(db, home_team.team_id, game_date)
            else:
                home_elo = ELO_INITIAL
                home_rolling = {'avg_pts_scored': 0, 'avg_pts_allowed': 0, 'avg_fg_pct': 0, 
                               'avg_rebounds': 0, 'avg_assists': 0, 'avg_tov': 0, 'avg_plus_minus': 0}
            home_offensive_rating = home_rolling.get('avg_pts_scored', 0)
            home_defensive_rating = home_rolling.get('avg_pts_allowed', 0)
        
        if away_stats:
            away_elo = away_stats['elo']
            away_offensive_rating = away_stats['offensive_rating']
            away_defensive_rating = away_stats['defensive_rating']
            away_rolling = {
                'avg_pts_scored': away_stats['avg_pts_scored_l10'],
                'avg_pts_allowed': away_stats['avg_pts_allowed_l10'],
                'avg_fg_pct': away_stats['avg_fg_pct_l10'],
                'avg_rebounds': away_stats['avg_rebounds_l10'],
                'avg_assists': away_stats['avg_assists_l10'],
                'avg_tov': away_stats['avg_tov_l10'],
                'avg_plus_minus': away_stats['avg_plus_minus_l10'],
            }
        else:
            # Fallback to database/defaults
            if away_team.team_id:
                away_elo = get_current_elo(db, away_team.team_id)
                away_rolling = get_rolling_averages(db, away_team.team_id, game_date)
            else:
                away_elo = ELO_INITIAL
                away_rolling = {'avg_pts_scored': 0, 'avg_pts_allowed': 0, 'avg_fg_pct': 0,
                               'avg_rebounds': 0, 'avg_assists': 0, 'avg_tov': 0, 'avg_plus_minus': 0}
            away_offensive_rating = away_rolling.get('avg_pts_scored', 0)
            away_defensive_rating = away_rolling.get('avg_pts_allowed', 0)
        
        # Get H2H from training dataset
        h2h_home, h2h_away = get_h2h_from_training_data(home_team_name, away_team_name, training_df, game_date)
        
        # Get rest days (fallback to default if not in database)
        if home_team.team_id:
            home_rest = get_days_rest(db, home_team.team_id, game_date)
        else:
            home_rest = 3  # Default
        if away_team.team_id:
            away_rest = get_days_rest(db, away_team.team_id, game_date)
        else:
            away_rest = 3  # Default
        
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

