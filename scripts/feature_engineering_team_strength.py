"""
Feature Engineering Script - Team Strength Focused
Reframes features to emphasize team strength (team1 vs team2) rather than home/away.
"""
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import warnings
import sys
warnings.filterwarnings('ignore')

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
INPUT_FILE = DATA_DIR / "training_dataset.csv"
OUTPUT_FILE = DATA_DIR / "training_dataset_engineered.csv"

# ELO parameters
ELO_INITIAL = 1500
ELO_K = 32  # K-factor for ELO updates

def print_progress(msg):
    """Print progress message with flush"""
    print(msg, flush=True)
    sys.stdout.flush()


def calculate_elo_ratings(df):
    """
    Calculate ELO ratings for each team over time.
    Updates ELO after each game based on result.
    """
    print_progress("\nCalculating ELO ratings...")
    
    # Sort by date to process chronologically
    df = df.sort_values('game_date').copy()
    
    # Initialize ELO dictionary
    elo_dict = {}
    
    # Track ELO for each game
    home_elo_list = []
    away_elo_list = []
    
    for idx, row in df.iterrows():
        home_team = row['home_team_id']
        away_team = row['away_team_id']
        home_score = row['home_score']
        away_score = row['away_score']
        
        # Initialize ELO if not exists
        if home_team not in elo_dict:
            elo_dict[home_team] = ELO_INITIAL
        if away_team not in elo_dict:
            elo_dict[away_team] = ELO_INITIAL
        
        # Get pre-game ELO
        home_elo_pre = elo_dict[home_team]
        away_elo_pre = elo_dict[away_team]
        
        home_elo_list.append(home_elo_pre)
        away_elo_list.append(away_elo_pre)
        
        # Calculate expected score
        expected_home = 1 / (1 + 10 ** ((away_elo_pre - home_elo_pre) / 400))
        expected_away = 1 - expected_home
        
        # Actual result (1 if home wins, 0 if away wins)
        actual_home = 1 if home_score > away_score else 0
        actual_away = 1 - actual_home
        
        # Update ELO
        elo_dict[home_team] = home_elo_pre + ELO_K * (actual_home - expected_home)
        elo_dict[away_team] = away_elo_pre + ELO_K * (actual_away - expected_away)
    
    df['home_elo'] = home_elo_list
    df['away_elo'] = away_elo_list
    
    print_progress(f"  Calculated ELO for {len(elo_dict)} unique teams")
    print_progress(f"  ELO range: {min(home_elo_list + away_elo_list):.1f} - {max(home_elo_list + away_elo_list):.1f}")
    
    return df


def calculate_rolling_averages(df, window=10):
    """
    Calculate rolling averages for key metrics (last N games).
    """
    print_progress(f"\nCalculating rolling averages (window={window})...")
    
    df = df.sort_values('game_date').copy()
    
    # Initialize rolling average columns
    rolling_cols = [
        'home_avg_pts_scored_l10', 'home_avg_pts_allowed_l10',
        'home_avg_fg_pct_l10', 'home_avg_rebounds_l10',
        'home_avg_assists_l10', 'home_avg_tov_l10', 'home_avg_plus_minus_l10',
        'away_avg_pts_scored_l10', 'away_avg_pts_allowed_l10',
        'away_avg_fg_pct_l10', 'away_avg_rebounds_l10',
        'away_avg_assists_l10', 'away_avg_tov_l10', 'away_avg_plus_minus_l10'
    ]
    
    for col in rolling_cols:
        df[col] = np.nan
    
    # For each team, calculate rolling stats
    all_teams = set(df['home_team_id'].unique()) | set(df['away_team_id'].unique())
    
    for team_id in all_teams:
        # Get all games where this team played (home or away)
        team_mask = (df['home_team_id'] == team_id) | (df['away_team_id'] == team_id)
        team_games = df[team_mask].copy()
        team_games = team_games.sort_values('game_date').reset_index()
        
        # Track team's stats across games
        team_stats_history = []
        
        for i, row in team_games.iterrows():
            game_idx = row['index']
            is_home = df.loc[game_idx, 'home_team_id'] == team_id
            
            # Calculate rolling averages from previous games
            if len(team_stats_history) > 0:
                # Get last N games
                last_n = team_stats_history[-window:] if len(team_stats_history) >= window else team_stats_history
                
                if len(last_n) > 0:
                    # Calculate averages
                    avg_pts_scored = np.mean([s['pts_scored'] for s in last_n])
                    avg_pts_allowed = np.mean([s['pts_allowed'] for s in last_n])
                    avg_fg_pct = np.mean([s['fg_pct'] for s in last_n if not np.isnan(s['fg_pct'])])
                    avg_rebounds = np.mean([s['rebounds'] for s in last_n if not np.isnan(s['rebounds'])])
                    avg_assists = np.mean([s['assists'] for s in last_n if not np.isnan(s['assists'])])
                    avg_tov = np.mean([s['tov'] for s in last_n if not np.isnan(s['tov'])])
                    avg_plus_minus = np.mean([s['plus_minus'] for s in last_n if not np.isnan(s['plus_minus'])])
                    
                    # Assign to appropriate columns
                    if is_home:
                        df.loc[game_idx, 'home_avg_pts_scored_l10'] = avg_pts_scored
                        df.loc[game_idx, 'home_avg_pts_allowed_l10'] = avg_pts_allowed
                        df.loc[game_idx, 'home_avg_fg_pct_l10'] = avg_fg_pct if not np.isnan(avg_fg_pct) else 0
                        df.loc[game_idx, 'home_avg_rebounds_l10'] = avg_rebounds if not np.isnan(avg_rebounds) else 0
                        df.loc[game_idx, 'home_avg_assists_l10'] = avg_assists if not np.isnan(avg_assists) else 0
                        df.loc[game_idx, 'home_avg_tov_l10'] = avg_tov if not np.isnan(avg_tov) else 0
                        df.loc[game_idx, 'home_avg_plus_minus_l10'] = avg_plus_minus if not np.isnan(avg_plus_minus) else 0
                    else:
                        df.loc[game_idx, 'away_avg_pts_scored_l10'] = avg_pts_scored
                        df.loc[game_idx, 'away_avg_pts_allowed_l10'] = avg_pts_allowed
                        df.loc[game_idx, 'away_avg_fg_pct_l10'] = avg_fg_pct if not np.isnan(avg_fg_pct) else 0
                        df.loc[game_idx, 'away_avg_rebounds_l10'] = avg_rebounds if not np.isnan(avg_rebounds) else 0
                        df.loc[game_idx, 'away_avg_assists_l10'] = avg_assists if not np.isnan(avg_assists) else 0
                        df.loc[game_idx, 'away_avg_tov_l10'] = avg_tov if not np.isnan(avg_tov) else 0
                        df.loc[game_idx, 'away_avg_plus_minus_l10'] = avg_plus_minus if not np.isnan(avg_plus_minus) else 0
            
            # Add current game stats to history (for next games)
            if is_home:
                team_stats_history.append({
                    'pts_scored': df.loc[game_idx, 'home_score'],
                    'pts_allowed': df.loc[game_idx, 'away_score'],
                    'fg_pct': df.loc[game_idx, 'home_fg_pct'] if 'home_fg_pct' in df.columns else np.nan,
                    'rebounds': df.loc[game_idx, 'home_rebounds_total'] if 'home_rebounds_total' in df.columns else np.nan,
                    'assists': df.loc[game_idx, 'home_assists'] if 'home_assists' in df.columns else np.nan,
                    'tov': df.loc[game_idx, 'home_turnovers'] if 'home_turnovers' in df.columns else np.nan,
                    'plus_minus': df.loc[game_idx, 'home_plus_minus'] if 'home_plus_minus' in df.columns else np.nan,
                })
            else:
                team_stats_history.append({
                    'pts_scored': df.loc[game_idx, 'away_score'],
                    'pts_allowed': df.loc[game_idx, 'home_score'],
                    'fg_pct': df.loc[game_idx, 'away_fg_pct'] if 'away_fg_pct' in df.columns else np.nan,
                    'rebounds': df.loc[game_idx, 'away_rebounds_total'] if 'away_rebounds_total' in df.columns else np.nan,
                    'assists': df.loc[game_idx, 'away_assists'] if 'away_assists' in df.columns else np.nan,
                    'tov': df.loc[game_idx, 'away_turnovers'] if 'away_turnovers' in df.columns else np.nan,
                    'plus_minus': df.loc[game_idx, 'away_plus_minus'] if 'away_plus_minus' in df.columns else np.nan,
                })
    
    # Fill NaN with 0 for first games
    for col in rolling_cols:
        df[col] = df[col].fillna(0)
    
    print_progress(f"  Calculated rolling averages for {len(rolling_cols)} features")
    
    return df


def calculate_h2h_records(df):
    """
    Calculate head-to-head win percentages between teams.
    """
    print_progress("\nCalculating head-to-head records...")
    
    df = df.sort_values('game_date').copy()
    
    # Track H2H records
    h2h_dict = {}  # (team1, team2) -> (wins, total_games)
    
    home_h2h = []
    away_h2h = []
    
    for idx, row in df.iterrows():
        home_team = row['home_team_id']
        away_team = row['away_team_id']
        home_won = row['home_team_won']
        
        # Create H2H key (always use smaller ID first for consistency)
        key1 = (min(home_team, away_team), max(home_team, away_team))
        key2 = (max(home_team, away_team), min(home_team, away_team))
        
        # Get previous H2H record
        if key1 in h2h_dict:
            wins, total = h2h_dict[key1]
        elif key2 in h2h_dict:
            wins, total = h2h_dict[key2]
        else:
            wins, total = 0, 0
        
        # Calculate win percentage (before this game)
        if total > 0:
            h2h_pct = wins / total
        else:
            h2h_pct = 0.5  # Default to 50% if no history
        
        # For home team: their win % vs away team
        if home_team < away_team:
            home_h2h.append(h2h_pct)
        else:
            home_h2h.append(1 - h2h_pct)
        
        # For away team: their win % vs home team
        if away_team < home_team:
            away_h2h.append(h2h_pct)
        else:
            away_h2h.append(1 - h2h_pct)
        
        # Update H2H record after this game
        if home_won:
            if home_team < away_team:
                if key1 not in h2h_dict:
                    h2h_dict[key1] = [0, 0]
                h2h_dict[key1][0] += 1
                h2h_dict[key1][1] += 1
            else:
                if key2 not in h2h_dict:
                    h2h_dict[key2] = [0, 0]
                h2h_dict[key2][1] += 1  # Away team (smaller ID) lost
                h2h_dict[key2][0] += 0
                h2h_dict[key2][1] += 1
        else:
            if home_team < away_team:
                if key1 not in h2h_dict:
                    h2h_dict[key1] = [0, 0]
                h2h_dict[key1][1] += 1  # Home team (smaller ID) lost
            else:
                if key2 not in h2h_dict:
                    h2h_dict[key2] = [0, 0]
                h2h_dict[key2][0] += 1
                h2h_dict[key2][1] += 1
    
    df['home_h2h_win_pct'] = home_h2h
    df['away_h2h_win_pct'] = away_h2h
    
    print_progress(f"  Calculated H2H records for {len(h2h_dict)} team pairs")
    
    return df


def calculate_rest_days(df):
    """
    Calculate rest days for each team (days since last game).
    """
    print_progress("\nCalculating rest days...")
    
    df = df.sort_values('game_date').copy()
    
    # Track last game date for each team
    last_game_date = {}
    
    home_rest = []
    away_rest = []
    
    for idx, row in df.iterrows():
        home_team = row['home_team_id']
        away_team = row['away_team_id']
        game_date = pd.to_datetime(row['game_date']).date()
        
        # Get rest days
        if home_team in last_game_date:
            home_rest_days = (game_date - last_game_date[home_team]).days
        else:
            home_rest_days = 3  # Default for first game
        
        if away_team in last_game_date:
            away_rest_days = (game_date - last_game_date[away_team]).days
        else:
            away_rest_days = 3  # Default for first game
        
        home_rest.append(home_rest_days)
        away_rest.append(away_rest_days)
        
        # Update last game date
        last_game_date[home_team] = game_date
        last_game_date[away_team] = game_date
    
    df['home_rest_days'] = home_rest
    df['away_rest_days'] = away_rest
    df['rest_advantage'] = df['home_rest_days'] - df['away_rest_days']
    
    print_progress(f"  Calculated rest days for {len(last_game_date)} teams")
    print_progress(f"  Average rest days: Home={np.mean(home_rest):.1f}, Away={np.mean(away_rest):.1f}")
    
    return df


def calculate_offensive_defensive_ratings(df):
    """
    Calculate offensive and defensive ratings for teams.
    Offensive rating: points scored per 100 possessions (approximated)
    Defensive rating: points allowed per 100 possessions (approximated)
    """
    print_progress("\nCalculating offensive/defensive ratings...")
    
    # Use rolling averages if available, otherwise use season averages
    if 'home_avg_pts_scored_l10' in df.columns:
        df['home_offensive_rating'] = df['home_avg_pts_scored_l10']
        df['home_defensive_rating'] = df['home_avg_pts_allowed_l10']
        df['away_offensive_rating'] = df['away_avg_pts_scored_l10']
        df['away_defensive_rating'] = df['away_avg_pts_allowed_l10']
    else:
        # Fallback: use current game stats (less ideal)
        df['home_offensive_rating'] = df['home_score']
        df['home_defensive_rating'] = df['away_score']
        df['away_offensive_rating'] = df['away_score']
        df['away_defensive_rating'] = df['home_score']
    
    print_progress("  Calculated offensive/defensive ratings")
    
    return df


def reframe_to_team_strength(df):
    """
    Reframe features to team1 vs team2 (team strength focused) rather than home/away.
    Creates a symmetric representation where team1 and team2 are compared.
    """
    print_progress("\nReframing features to team strength format...")
    
    # Create new dataframe with team1 vs team2 structure
    rows = []
    
    for idx, row in df.iterrows():
        # Row 1: Home team as team1, Away team as team2
        team1_row = {
            # Identifiers
            'game_id': row['game_id'],
            'game_date': row['game_date'],
            'season': row['season'],
            
            # Teams
            'team1_id': row['home_team_id'],
            'team1_name': row.get('home_team_name', ''),
            'team2_id': row['away_team_id'],
            'team2_name': row.get('away_team_name', ''),
            
            # Target (home team won)
            'home_team_won': row['home_team_won'],
            'team1_won': row['home_team_won'],  # team1 is home, so same as home_team_won
            'team1_score': row['home_score'],
            'team2_score': row['away_score'],
            
            # Home advantage
            'is_home': 1,  # team1 is home
            
            # Team strength features
            'team1_elo': row.get('home_elo', ELO_INITIAL),
            'team2_elo': row.get('away_elo', ELO_INITIAL),
            'elo_diff': row.get('home_elo', ELO_INITIAL) - row.get('away_elo', ELO_INITIAL),
            
            # Offensive/Defensive ratings
            'team1_offensive_rating': row.get('home_offensive_rating', 0),
            'team1_defensive_rating': row.get('home_defensive_rating', 0),
            'team2_offensive_rating': row.get('away_offensive_rating', 0),
            'team2_defensive_rating': row.get('away_defensive_rating', 0),
            
            # Recent form (rolling averages)
            'team1_avg_pts_scored_l10': row.get('home_avg_pts_scored_l10', 0),
            'team1_avg_pts_allowed_l10': row.get('home_avg_pts_allowed_l10', 0),
            'team1_avg_fg_pct_l10': row.get('home_avg_fg_pct_l10', 0),
            'team1_avg_rebounds_l10': row.get('home_avg_rebounds_l10', 0),
            'team1_avg_assists_l10': row.get('home_avg_assists_l10', 0),
            'team1_avg_tov_l10': row.get('home_avg_tov_l10', 0),
            'team1_avg_plus_minus_l10': row.get('home_avg_plus_minus_l10', 0),
            
            'team2_avg_pts_scored_l10': row.get('away_avg_pts_scored_l10', 0),
            'team2_avg_pts_allowed_l10': row.get('away_avg_pts_allowed_l10', 0),
            'team2_avg_fg_pct_l10': row.get('away_avg_fg_pct_l10', 0),
            'team2_avg_rebounds_l10': row.get('away_avg_rebounds_l10', 0),
            'team2_avg_assists_l10': row.get('away_avg_assists_l10', 0),
            'team2_avg_tov_l10': row.get('away_avg_tov_l10', 0),
            'team2_avg_plus_minus_l10': row.get('away_avg_plus_minus_l10', 0),
            
            # Head-to-head
            'team1_h2h_win_pct': row.get('home_h2h_win_pct', 0.5),
            'team2_h2h_win_pct': row.get('away_h2h_win_pct', 0.5),
            
            # Rest days
            'team1_rest_days': row.get('home_rest_days', 3),
            'team2_rest_days': row.get('away_rest_days', 3),
            'rest_advantage': row.get('rest_advantage', 0),
            
            # Strength differentials
            'offensive_rating_diff': row.get('home_offensive_rating', 0) - row.get('away_offensive_rating', 0),
            'defensive_rating_diff': row.get('away_defensive_rating', 0) - row.get('home_defensive_rating', 0),  # Lower is better for defense
            'pts_scored_diff_l10': row.get('home_avg_pts_scored_l10', 0) - row.get('away_avg_pts_scored_l10', 0),
            'pts_allowed_diff_l10': row.get('away_avg_pts_allowed_l10', 0) - row.get('home_avg_pts_allowed_l10', 0),  # Lower is better
            'plus_minus_diff_l10': row.get('home_avg_plus_minus_l10', 0) - row.get('away_avg_plus_minus_l10', 0),
        }
        
        rows.append(team1_row)
        
        # Row 2: Away team as team1, Home team as team2 (for data augmentation)
        # This helps the model learn symmetric relationships
        team2_row = {
            # Identifiers
            'game_id': row['game_id'],
            'game_date': row['game_date'],
            'season': row['season'],
            
            # Teams (swapped)
            'team1_id': row['away_team_id'],
            'team1_name': row.get('away_team_name', ''),
            'team2_id': row['home_team_id'],
            'team2_name': row.get('home_team_name', ''),
            
            # Target (inverted - team1 is now away, so if home won, team1 lost)
            'home_team_won': row['home_team_won'],
            'team1_won': 1 - row['home_team_won'],  # Inverted
            'team1_score': row['away_score'],
            'team2_score': row['home_score'],
            
            # Home advantage (team1 is away now)
            'is_home': 0,
            
            # Team strength features (swapped)
            'team1_elo': row.get('away_elo', ELO_INITIAL),
            'team2_elo': row.get('home_elo', ELO_INITIAL),
            'elo_diff': row.get('away_elo', ELO_INITIAL) - row.get('home_elo', ELO_INITIAL),
            
            # Offensive/Defensive ratings (swapped)
            'team1_offensive_rating': row.get('away_offensive_rating', 0),
            'team1_defensive_rating': row.get('away_defensive_rating', 0),
            'team2_offensive_rating': row.get('home_offensive_rating', 0),
            'team2_defensive_rating': row.get('home_defensive_rating', 0),
            
            # Recent form (swapped)
            'team1_avg_pts_scored_l10': row.get('away_avg_pts_scored_l10', 0),
            'team1_avg_pts_allowed_l10': row.get('away_avg_pts_allowed_l10', 0),
            'team1_avg_fg_pct_l10': row.get('away_avg_fg_pct_l10', 0),
            'team1_avg_rebounds_l10': row.get('away_avg_rebounds_l10', 0),
            'team1_avg_assists_l10': row.get('away_avg_assists_l10', 0),
            'team1_avg_tov_l10': row.get('away_avg_tov_l10', 0),
            'team1_avg_plus_minus_l10': row.get('away_avg_plus_minus_l10', 0),
            
            'team2_avg_pts_scored_l10': row.get('home_avg_pts_scored_l10', 0),
            'team2_avg_pts_allowed_l10': row.get('home_avg_pts_allowed_l10', 0),
            'team2_avg_fg_pct_l10': row.get('home_avg_fg_pct_l10', 0),
            'team2_avg_rebounds_l10': row.get('home_avg_rebounds_l10', 0),
            'team2_avg_assists_l10': row.get('home_avg_assists_l10', 0),
            'team2_avg_tov_l10': row.get('home_avg_tov_l10', 0),
            'team2_avg_plus_minus_l10': row.get('home_avg_plus_minus_l10', 0),
            
            # Head-to-head (swapped)
            'team1_h2h_win_pct': row.get('away_h2h_win_pct', 0.5),
            'team2_h2h_win_pct': row.get('home_h2h_win_pct', 0.5),
            
            # Rest days (swapped)
            'team1_rest_days': row.get('away_rest_days', 3),
            'team2_rest_days': row.get('home_rest_days', 3),
            'rest_advantage': -row.get('rest_advantage', 0),  # Inverted
            
            # Strength differentials (inverted)
            'offensive_rating_diff': row.get('away_offensive_rating', 0) - row.get('home_offensive_rating', 0),
            'defensive_rating_diff': row.get('home_defensive_rating', 0) - row.get('away_defensive_rating', 0),
            'pts_scored_diff_l10': row.get('away_avg_pts_scored_l10', 0) - row.get('home_avg_pts_scored_l10', 0),
            'pts_allowed_diff_l10': row.get('home_avg_pts_allowed_l10', 0) - row.get('away_avg_pts_allowed_l10', 0),
            'plus_minus_diff_l10': row.get('away_avg_plus_minus_l10', 0) - row.get('home_avg_plus_minus_l10', 0),
        }
        
        rows.append(team2_row)
    
    new_df = pd.DataFrame(rows)
    
    print_progress(f"  Reframed {len(df)} games to {len(new_df)} rows (2x for symmetry)")
    print_progress(f"  Features: {len(new_df.columns)} columns")
    
    return new_df


def main():
    """Main feature engineering pipeline"""
    print_progress("=" * 80)
    print_progress("FEATURE ENGINEERING - TEAM STRENGTH FOCUSED")
    print_progress("=" * 80)
    
    try:
        # Step 1: Load training dataset
        print_progress("\n[Step 1/7] Loading training dataset...")
        if not INPUT_FILE.exists():
            raise FileNotFoundError(f"Training dataset not found: {INPUT_FILE}")
        
        df = pd.read_csv(INPUT_FILE, low_memory=False)
        df['game_date'] = pd.to_datetime(df['game_date'])
        print_progress(f"  Loaded {len(df):,} games, {len(df.columns)} columns")
        
        # Step 2: Calculate ELO ratings
        print_progress("\n[Step 2/7] Calculating ELO ratings...")
        df = calculate_elo_ratings(df)
        
        # Step 3: Calculate rolling averages
        print_progress("\n[Step 3/7] Calculating rolling averages...")
        df = calculate_rolling_averages(df, window=10)
        
        # Step 4: Calculate H2H records
        print_progress("\n[Step 4/7] Calculating head-to-head records...")
        df = calculate_h2h_records(df)
        
        # Step 5: Calculate rest days
        print_progress("\n[Step 5/7] Calculating rest days...")
        df = calculate_rest_days(df)
        
        # Step 6: Calculate offensive/defensive ratings
        print_progress("\n[Step 6/7] Calculating offensive/defensive ratings...")
        df = calculate_offensive_defensive_ratings(df)
        
        # Step 7: Reframe to team strength format
        print_progress("\n[Step 7/7] Reframing to team strength format...")
        df_final = reframe_to_team_strength(df)
        
        # Save final dataset
        print_progress("\nSaving engineered dataset...")
        OUTPUT_FILE.parent.mkdir(exist_ok=True)
        df_final.to_csv(OUTPUT_FILE, index=False)
        
        print_progress(f"\n{'='*80}")
        print_progress("FEATURE ENGINEERING COMPLETE!")
        print_progress(f"{'='*80}")
        print_progress(f"\nFinal dataset saved to: {OUTPUT_FILE}")
        print_progress(f"  - Rows: {len(df_final):,}")
        print_progress(f"  - Columns: {len(df_final.columns)}")
        print_progress(f"  - Unique games: {df_final['game_id'].nunique():,}")
        
        # Show feature summary
        print_progress("\nFeature Categories:")
        print_progress(f"  - Team Strength: ELO ratings, offensive/defensive ratings")
        print_progress(f"  - Recent Form: Rolling averages (last 10 games)")
        print_progress(f"  - Head-to-Head: Win percentages between teams")
        print_progress(f"  - Rest Days: Days since last game")
        print_progress(f"  - Home Advantage: is_home feature (separate from team strength)")
        print_progress(f"  - Target: home_team_won (which team won)")
        
        # Show sample
        print_progress("\nSample features:")
        feature_cols = [col for col in df_final.columns if col not in 
                       ['game_id', 'game_date', 'season', 'team1_id', 'team1_name', 
                        'team2_id', 'team2_name', 'team1_score', 'team2_score']]
        print_progress(f"  {', '.join(feature_cols[:10])}...")
        
        return df_final
        
    except Exception as e:
        print_progress(f"\nERROR: {str(e)}")
        import traceback
        print_progress(traceback.format_exc())
        raise


if __name__ == "__main__":
    df = main()

