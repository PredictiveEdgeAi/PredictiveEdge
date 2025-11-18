"""
Feature engineering module for NBA Predictor.
Handles ELO calculation and feature set creation.
"""
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.database import get_session, Game, Team, TeamBoxScore
from src.config import (
    ELO_INITIAL, ELO_K_FACTOR, ELO_HOME_ADVANTAGE, ROLLING_WINDOW
)
from datetime import datetime, timedelta
from typing import Dict, Optional


def calculate_elo_ratings(db: Session):
    """
    Calculate ELO ratings for all teams chronologically.
    Updates games table with pre-game ELO ratings.
    """
    print("Calculating ELO ratings...")
    
    # Initialize ELO dictionary
    elo_ratings: Dict[int, float] = {}
    
    # Get all teams and initialize ELO
    teams = db.query(Team).all()
    for team in teams:
        elo_ratings[team.team_id] = ELO_INITIAL
    
    # Get all games ordered by date
    games = db.query(Game).order_by(Game.date, Game.game_id).all()
    
    updated_count = 0
    for game in games:
        home_team_id = game.home_team_id
        away_team_id = game.away_team_id
        
        # Get current ELO ratings
        home_elo = elo_ratings[home_team_id]
        away_elo = elo_ratings[away_team_id]
        
        # Store pre-game ELOs
        game.home_team_pregame_elo = home_elo
        game.away_team_pregame_elo = away_elo
        
        # Calculate expected win probability
        # Add home advantage to home team ELO
        home_elo_with_advantage = home_elo + ELO_HOME_ADVANTAGE
        
        # Expected win probability for home team
        expected_home_win = 1 / (1 + 10 ** ((away_elo - home_elo_with_advantage) / 400))
        expected_away_win = 1 - expected_home_win
        
        # Update ELO if game result is available
        if game.home_score is not None and game.away_score is not None:
            # Actual result: 1 if home wins, 0 if away wins
            if game.home_score > game.away_score:
                actual_home_score = 1.0
                actual_away_score = 0.0
            elif game.home_score < game.away_score:
                actual_home_score = 0.0
                actual_away_score = 1.0
            else:
                # Tie (rare in NBA)
                actual_home_score = 0.5
                actual_away_score = 0.5
            
            # Update ELO ratings
            home_elo_change = ELO_K_FACTOR * (actual_home_score - expected_home_win)
            away_elo_change = ELO_K_FACTOR * (actual_away_score - expected_away_win)
            
            elo_ratings[home_team_id] = home_elo + home_elo_change
            elo_ratings[away_team_id] = away_elo + away_elo_change
        
        updated_count += 1
    
    # Commit all ELO updates
    db.commit()
    print(f"Updated ELO ratings for {updated_count} games.")


def get_rolling_averages(
    db: Session,
    team_id: int,
    game_date: datetime.date,
    window: int = ROLLING_WINDOW
) -> Dict[str, float]:
    """
    Calculate rolling averages for a team up to (but not including) a specific game date.
    
    Returns:
        Dictionary with rolling average statistics
    """
    # Get team's box scores before the game date
    box_scores = db.query(TeamBoxScore).join(Game).filter(
        TeamBoxScore.team_id == team_id,
        Game.date < game_date,
        Game.home_score.isnot(None)  # Only completed games
    ).order_by(Game.date.desc()).limit(window).all()
    
    if not box_scores:
        # Return default values if no history
        return {
            'avg_pts_scored': 0.0,
            'avg_pts_allowed': 0.0,
            'avg_fg_pct': 0.0,
            'avg_tov': 0.0,
            'avg_plus_minus': 0.0,
            'avg_rebounds': 0.0,
            'avg_assists': 0.0
        }
    
    # Calculate averages
    total_pts = sum(bs.pts for bs in box_scores)
    total_fg_pct = sum(bs.fg_pct for bs in box_scores)
    total_tov = sum(bs.tov for bs in box_scores)
    total_plus_minus = sum(bs.plus_minus for bs in box_scores)
    total_rebounds = sum(bs.trb for bs in box_scores)
    total_assists = sum(bs.ast for bs in box_scores)
    
    n = len(box_scores)
    
    # Calculate points allowed (need to get opponent scores)
    total_pts_allowed = 0
    for bs in box_scores:
        game = bs.game
        if bs.is_home:
            total_pts_allowed += game.away_score or 0
        else:
            total_pts_allowed += game.home_score or 0
    
    return {
        'avg_pts_scored': total_pts / n if n > 0 else 0.0,
        'avg_pts_allowed': total_pts_allowed / n if n > 0 else 0.0,
        'avg_fg_pct': total_fg_pct / n if n > 0 else 0.0,
        'avg_tov': total_tov / n if n > 0 else 0.0,
        'avg_plus_minus': total_plus_minus / n if n > 0 else 0.0,
        'avg_rebounds': total_rebounds / n if n > 0 else 0.0,
        'avg_assists': total_assists / n if n > 0 else 0.0
    }


def get_h2h_win_pct(db: Session, team_id: int, opponent_id: int, game_date: datetime.date) -> float:
    """
    Calculate head-to-head win percentage for team_id vs opponent_id before game_date.
    """
    # Get all previous games between these teams
    games = db.query(Game).filter(
        ((Game.home_team_id == team_id) & (Game.away_team_id == opponent_id)) |
        ((Game.home_team_id == opponent_id) & (Game.away_team_id == team_id)),
        Game.date < game_date,
        Game.home_score.isnot(None)
    ).all()
    
    if not games:
        return 0.5  # Default to 50% if no history
    
    wins = 0
    for game in games:
        if game.home_score is None or game.away_score is None:
            continue
        
        if (game.home_team_id == team_id and game.home_score > game.away_score) or \
           (game.away_team_id == team_id and game.away_score > game.home_score):
            wins += 1
    
    return wins / len(games) if len(games) > 0 else 0.5


def get_days_rest(db: Session, team_id: int, game_date: datetime.date) -> int:
    """
    Calculate days since last game for a team.
    """
    last_game = db.query(Game).join(TeamBoxScore).filter(
        TeamBoxScore.team_id == team_id,
        Game.date < game_date,
        Game.home_score.isnot(None)
    ).order_by(Game.date.desc()).first()
    
    if not last_game:
        return 3  # Default to 3 days if no history
    
    days_rest = (game_date - last_game.date).days
    return max(0, days_rest)  # Ensure non-negative


def create_feature_set(db: Session, season_filter: Optional[int] = None) -> pd.DataFrame:
    """
    Create the complete feature set for training.
    One row = one team's perspective of one game.
    
    Args:
        db: Database session
        season_filter: Optional season to filter by (None = all seasons)
    
    Returns:
        DataFrame with features and targets
    """
    print("Creating feature set...")
    
    # Get all completed games
    query = db.query(Game).filter(Game.home_score.isnot(None))
    if season_filter:
        query = query.filter(Game.season == season_filter)
    
    games = query.order_by(Game.date).all()
    
    rows = []
    
    for game in games:
        if game.home_score is None or game.away_score is None:
            continue
        
        # Determine winner
        home_won = 1 if game.home_score > game.away_score else 0
        win_margin = game.home_score - game.away_score
        
        # Get ELO ratings (should be pre-calculated)
        home_elo = game.home_team_pregame_elo or ELO_INITIAL
        away_elo = game.away_team_pregame_elo or ELO_INITIAL
        
        # Get rolling averages
        home_rolling = get_rolling_averages(db, game.home_team_id, game.date)
        away_rolling = get_rolling_averages(db, game.away_team_id, game.date)
        
        # Get H2H
        h2h_home = get_h2h_win_pct(db, game.home_team_id, game.away_team_id, game.date)
        h2h_away = get_h2h_win_pct(db, game.away_team_id, game.home_team_id, game.date)
        
        # Get rest days
        home_rest = get_days_rest(db, game.home_team_id, game.date)
        away_rest = get_days_rest(db, game.away_team_id, game.date)
        
        # Create row from home team perspective
        home_row = {
            'game_id': game.game_id,
            'team_id': game.home_team_id,
            'opponent_id': game.away_team_id,
            'is_home': 1,
            'target_did_win': home_won,
            'target_win_margin': win_margin,
            # ELO features
            'team_elo': home_elo,
            'opponent_elo': away_elo,
            'elo_diff': home_elo - away_elo,
            # Team form (rolling averages)
            'avg_pts_scored_l10': home_rolling['avg_pts_scored'],
            'avg_pts_allowed_l10': home_rolling['avg_pts_allowed'],
            'avg_fg_pct_l10': home_rolling['avg_fg_pct'],
            'avg_tov_l10': home_rolling['avg_tov'],
            'avg_plus_minus_l10': home_rolling['avg_plus_minus'],
            'avg_rebounds_l10': home_rolling['avg_rebounds'],
            'avg_assists_l10': home_rolling['avg_assists'],
            # Opponent form
            'opp_avg_pts_scored_l10': away_rolling['avg_pts_scored'],
            'opp_avg_pts_allowed_l10': away_rolling['avg_pts_allowed'],
            'opp_avg_fg_pct_l10': away_rolling['avg_fg_pct'],
            'opp_avg_tov_l10': away_rolling['avg_tov'],
            'opp_avg_plus_minus_l10': away_rolling['avg_plus_minus'],
            # H2H
            'h2h_win_pct': h2h_home,
            # Rest
            'days_since_last_game': home_rest,
            'opponent_days_since_last_game': away_rest,
            'rest_advantage': home_rest - away_rest,
            # Season
            'season': game.season,
            'date': game.date
        }
        rows.append(home_row)
        
        # Create row from away team perspective
        away_row = {
            'game_id': game.game_id,
            'team_id': game.away_team_id,
            'opponent_id': game.home_team_id,
            'is_home': 0,
            'target_did_win': 1 - home_won,
            'target_win_margin': -win_margin,
            # ELO features
            'team_elo': away_elo,
            'opponent_elo': home_elo,
            'elo_diff': away_elo - home_elo,
            # Team form
            'avg_pts_scored_l10': away_rolling['avg_pts_scored'],
            'avg_pts_allowed_l10': away_rolling['avg_pts_allowed'],
            'avg_fg_pct_l10': away_rolling['avg_fg_pct'],
            'avg_tov_l10': away_rolling['avg_tov'],
            'avg_plus_minus_l10': away_rolling['avg_plus_minus'],
            'avg_rebounds_l10': away_rolling['avg_rebounds'],
            'avg_assists_l10': away_rolling['avg_assists'],
            # Opponent form
            'opp_avg_pts_scored_l10': home_rolling['avg_pts_scored'],
            'opp_avg_pts_allowed_l10': home_rolling['avg_pts_allowed'],
            'opp_avg_fg_pct_l10': home_rolling['avg_fg_pct'],
            'opp_avg_tov_l10': home_rolling['avg_tov'],
            'opp_avg_plus_minus_l10': home_rolling['avg_plus_minus'],
            # H2H
            'h2h_win_pct': h2h_away,
            # Rest
            'days_since_last_game': away_rest,
            'opponent_days_since_last_game': home_rest,
            'rest_advantage': away_rest - home_rest,
            # Season
            'season': game.season,
            'date': game.date
        }
        rows.append(away_row)
    
    df = pd.DataFrame(rows)
    print(f"Created feature set with {len(df)} rows.")
    return df


if __name__ == "__main__":
    db = get_session()
    try:
        # Calculate ELO ratings first
        calculate_elo_ratings(db)
        
        # Create feature set
        df = create_feature_set(db)
        print(f"Feature set shape: {df.shape}")
        print(f"Columns: {df.columns.tolist()}")
        
        # Save to CSV for inspection
        df.to_csv("data/features.csv", index=False)
        print("Feature set saved to data/features.csv")
        
    finally:
        db.close()

