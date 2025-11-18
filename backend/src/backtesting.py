"""
Backtesting module for NBA Predictor.
Simulates betting strategy to evaluate profitability.
"""
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from src.config import MODEL_ARTIFACTS_DIR, VALUE_EDGE_THRESHOLD, TEST_SEASON
from src.database import get_session, Game, Odds
from src.feature_engineering import create_feature_set
from src.training import FEATURE_COLUMNS, split_data_temporally, scale_data


def moneyline_to_implied_prob(moneyline: int) -> float:
    """
    Convert American moneyline odds to implied probability.
    
    Args:
        moneyline: American odds (e.g., -150 or +130)
    
    Returns:
        Implied probability (0.0 to 1.0)
    """
    if moneyline > 0:
        return 100 / (moneyline + 100)
    else:
        return abs(moneyline) / (abs(moneyline) + 100)


def moneyline_to_payout(moneyline: int, bet_amount: float = 100.0) -> float:
    """
    Calculate payout for a winning bet.
    
    Args:
        moneyline: American odds
        bet_amount: Amount bet (default $100)
    
    Returns:
        Total payout (including original bet)
    """
    if moneyline > 0:
        return bet_amount * (1 + moneyline / 100)
    else:
        return bet_amount * (1 + 100 / abs(moneyline))


def run_profitability_simulation(
    model,
    scaler,
    features_df: pd.DataFrame,
    test_season: int = TEST_SEASON,
    edge_threshold: float = VALUE_EDGE_THRESHOLD,
    bet_amount: float = 100.0
):
    """
    Run profitability simulation on test set.
    
    Args:
        model: Trained model
        scaler: Fitted StandardScaler
        features_df: Full feature dataframe
        test_season: Season to test on
        edge_threshold: Minimum edge required to place bet (default 3%)
        bet_amount: Amount to bet per game (default $100)
    
    Returns:
        Dictionary with simulation results
    """
    print("=" * 60)
    print("Running Profitability Simulation")
    print("=" * 60)
    
    # Filter to test season
    test_df = features_df[features_df['season'] == test_season].copy()
    
    if len(test_df) == 0:
        print(f"No data found for season {test_season}")
        return None
    
    # Get test features and targets
    X_test = test_df[FEATURE_COLUMNS].values
    y_test = test_df['target_did_win'].values
    X_test_scaled = scaler.transform(X_test)
    
    # Get model probabilities
    model_proba = model.predict_proba(X_test_scaled)
    model_win_proba = model_proba[:, 1]  # Probability of team winning
    
    # Get odds data
    db = get_session()
    try:
        # Get games with odds
        game_ids = test_df['game_id'].unique()
        odds_query = db.query(Odds).filter(Odds.game_id.in_(game_ids)).all()
        
        # Create odds lookup
        odds_dict = {}
        for odds in odds_query:
            if odds.game_id not in odds_dict:
                odds_dict[odds.game_id] = []
            odds_dict[odds.game_id].append(odds)
        
    finally:
        db.close()
    
    # Simulate betting
    total_bets = 0
    total_won = 0
    total_profit = 0.0
    bets_placed = []
    
    for idx, row in test_df.iterrows():
        game_id = row['game_id']
        is_home = row['is_home']
        team_id = row['team_id']
        opponent_id = row['opponent_id']
        actual_win = row['target_did_win']
        model_prob = model_win_proba[test_df.index.get_loc(idx)]
        
        # Get odds for this game
        if game_id not in odds_dict or len(odds_dict[game_id]) == 0:
            continue  # Skip if no odds available
        
        # Use first available odds (could be enhanced to use best odds)
        odds = odds_dict[game_id][0]
        
        # Determine which team we're betting on
        if is_home:
            moneyline = odds.home_team_moneyline
        else:
            moneyline = odds.away_team_moneyline
        
        if moneyline is None:
            continue
        
        # Calculate implied probability
        implied_prob = moneyline_to_implied_prob(moneyline)
        
        # Check for value bet
        edge = model_prob - implied_prob
        
        if edge > edge_threshold:
            # Place bet
            total_bets += 1
            
            # Calculate profit/loss
            if actual_win == 1:
                payout = moneyline_to_payout(moneyline, bet_amount)
                profit = payout - bet_amount
                total_profit += profit
                total_won += 1
                result = "WIN"
            else:
                profit = -bet_amount
                total_profit += profit
                result = "LOSS"
            
            bets_placed.append({
                'game_id': game_id,
                'team_id': team_id,
                'opponent_id': opponent_id,
                'is_home': is_home,
                'model_prob': model_prob,
                'implied_prob': implied_prob,
                'edge': edge,
                'moneyline': moneyline,
                'result': result,
                'profit': profit
            })
    
    # Calculate metrics
    win_rate = (total_won / total_bets * 100) if total_bets > 0 else 0
    roi = (total_profit / (total_bets * bet_amount) * 100) if total_bets > 0 else 0
    
    # Print results
    print(f"\nSimulation Results:")
    print(f"  Test Season: {test_season}")
    print(f"  Edge Threshold: {edge_threshold * 100:.1f}%")
    print(f"  Bet Amount: ${bet_amount:.2f}")
    print(f"  Total Games Available: {len(test_df)}")
    print(f"  Total Bets Placed: {total_bets}")
    print(f"  Total Won: {total_won}")
    print(f"  Total Lost: {total_bets - total_won}")
    print(f"  Win Rate: {win_rate:.2f}%")
    print(f"  Total Profit/Loss: ${total_profit:.2f}")
    print(f"  Return on Investment (ROI): {roi:.2f}%")
    
    if total_bets > 0:
        avg_profit_per_bet = total_profit / total_bets
        print(f"  Average Profit per Bet: ${avg_profit_per_bet:.2f}")
    
    # Save detailed results
    if bets_placed:
        bets_df = pd.DataFrame(bets_placed)
        results_path = MODEL_ARTIFACTS_DIR / "backtest_results.csv"
        bets_df.to_csv(results_path, index=False)
        print(f"\nDetailed results saved to {results_path}")
    
    return {
        'total_bets': total_bets,
        'total_won': total_won,
        'total_lost': total_bets - total_won,
        'win_rate': win_rate,
        'total_profit': total_profit,
        'roi': roi,
        'bets_placed': bets_placed
    }


def run_backtest():
    """
    Complete backtesting pipeline.
    """
    print("Loading model and scaler...")
    
    # Load model and scaler
    model_path = MODEL_ARTIFACTS_DIR / "best_model.joblib"
    scaler_path = MODEL_ARTIFACTS_DIR / "data_scaler.joblib"
    
    if not model_path.exists() or not scaler_path.exists():
        print("Error: Model or scaler not found. Please run training first.")
        return
    
    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)
    
    # Create feature set
    print("Creating feature set...")
    db = get_session()
    try:
        from src.feature_engineering import calculate_elo_ratings
        calculate_elo_ratings(db)
        features_df = create_feature_set(db)
    finally:
        db.close()
    
    # Run simulation
    results = run_profitability_simulation(model, scaler, features_df)
    
    return results


if __name__ == "__main__":
    run_backtest()

