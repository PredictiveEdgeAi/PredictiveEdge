"""
Fixed data preparation script - uses game.csv as primary source for historical data.
Merges detailed stats from TeamStatistics.csv where available.
"""
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import warnings
import sys
warnings.filterwarnings('ignore')

# Configuration - paths relative to project root (one level up from scripts/)
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "Kaggle Datasets"
OUTPUT_DIR = PROJECT_ROOT / "data"
OUTPUT_FILE = OUTPUT_DIR / "training_dataset.csv"

def print_progress(msg):
    """Print progress message with flush"""
    print(msg, flush=True)
    sys.stdout.flush()

def load_game_data():
    """Load game.csv - primary source for historical games with scores"""
    print_progress("Loading game.csv (primary source)...")
    file_path = DATA_DIR / "csv" / "game.csv"
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    df = pd.read_csv(file_path, low_memory=False)
    print_progress(f"  Loaded {len(df):,} rows, {len(df.columns)} columns")
    
    # Convert date - check for different column name variations
    date_col = None
    for col in ['game_date', 'game_date_est']:
        if col in df.columns:
            date_col = col
            break
    
    if date_col:
        df['game_date'] = pd.to_datetime(df[date_col], errors='coerce')
        
        # Extract season (NBA season starts in October)
        df['season'] = df['game_date'].apply(
            lambda x: x.year if pd.notna(x) and x.month >= 10 else (x.year - 1 if pd.notna(x) else None)
        )
    
    # Rename columns to standardize - game.csv has different column names
    rename_map = {}
    
    # Game ID - already correct
    # Date - already handled above as 'game_date'
    
    # Team IDs
    if 'team_id_home' in df.columns:
        rename_map['team_id_home'] = 'home_team_id'
    if 'team_id_away' in df.columns:
        rename_map['team_id_away'] = 'away_team_id'
    
    # Scores
    if 'pts_home' in df.columns:
        rename_map['pts_home'] = 'home_score'
    if 'pts_away' in df.columns:
        rename_map['pts_away'] = 'away_score'
    
    # Team names - game.csv uses team_name_home/away
    if 'team_name_home' in df.columns:
        rename_map['team_name_home'] = 'home_team_name'
    elif 'team_nickname_home' in df.columns:
        rename_map['team_nickname_home'] = 'home_team_name'
    
    if 'team_name_away' in df.columns:
        rename_map['team_name_away'] = 'away_team_name'
    elif 'team_nickname_away' in df.columns:
        rename_map['team_nickname_away'] = 'away_team_name'
    
    # Team cities (may not exist in game.csv)
    if 'team_city_name_home' in df.columns:
        rename_map['team_city_name_home'] = 'home_team_city'
    if 'team_city_name_away' in df.columns:
        rename_map['team_city_name_away'] = 'away_team_city'
    
    # Only rename columns that exist
    rename_map = {k: v for k, v in rename_map.items() if k in df.columns}
    df = df.rename(columns=rename_map)
    
    # Ensure game_id is string for consistent merging
    if 'game_id' in df.columns:
        df['game_id'] = df['game_id'].astype(str)
    
    # Filter to games with scores (be less aggressive - allow some missing data)
    if 'home_score' in df.columns and 'away_score' in df.columns:
        before = len(df)
        # Only require that scores exist and are reasonable (not necessarily > 0, as some old games might have 0)
        df = df[
            (df['home_score'].notna()) & 
            (df['away_score'].notna()) &
            (df['home_score'] >= 0) &  # Allow 0 scores for very old games
            (df['away_score'] >= 0) &
            (df['home_score'] <= 200) &  # Remove obvious outliers
            (df['away_score'] <= 200)
        ].copy()
        print_progress(f"  Filtered to {len(df):,} games with scores (from {before:,})")
    
    # Add target variable
    if 'home_score' in df.columns and 'away_score' in df.columns:
        df['home_team_won'] = (df['home_score'] > df['away_score']).astype(int)
    
    print_progress(f"  Date range: {df['game_date'].min()} to {df['game_date'].max()}")
    if 'season' in df.columns:
        print_progress(f"  Seasons: {df['season'].min()} to {df['season'].max()}")
    
    return df


def load_team_statistics():
    """Load TeamStatistics.csv - detailed stats (may have missing data)"""
    print_progress("\nLoading TeamStatistics.csv (for detailed stats)...")
    file_path = DATA_DIR / "Basketball" / "TeamStatistics.csv"
    
    if not file_path.exists():
        print_progress("  Warning: TeamStatistics.csv not found, skipping...")
        return pd.DataFrame()
    
    df = pd.read_csv(file_path, low_memory=False)
    print_progress(f"  Loaded {len(df):,} rows")
    
    # Convert gameDate to datetime
    if 'gameDate' in df.columns:
        df['gameDate'] = pd.to_datetime(df['gameDate'], errors='coerce')
    
    # Clean numeric columns
    numeric_cols = ['teamScore', 'opponentScore', 'assists', 'blocks', 'steals', 
                    'fieldGoalsMade', 'fieldGoalsAttempted', 'fieldGoalsPercentage',
                    'threePointersMade', 'threePointersAttempted', 'threePointersPercentage',
                    'freeThrowsMade', 'freeThrowsAttempted', 'freeThrowsPercentage',
                    'reboundsTotal', 'reboundsOffensive', 'reboundsDefensive',
                    'turnovers', 'foulsPersonal', 'plusMinusPoints',
                    'q1Points', 'q2Points', 'q3Points', 'q4Points',
                    'seasonWins', 'seasonLosses']
    
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Fix percentages > 1
    for pct_col in ['fieldGoalsPercentage', 'threePointersPercentage', 'freeThrowsPercentage']:
        if pct_col in df.columns:
            mask = df[pct_col] > 1
            df.loc[mask, pct_col] /= 100
    
    return df


def load_other_stats():
    """Load other_stats.csv for advanced metrics"""
    print_progress("\nLoading other_stats.csv...")
    file_path = DATA_DIR / "csv" / "other_stats.csv"
    
    if not file_path.exists():
        print_progress("  Warning: other_stats.csv not found, skipping...")
        return pd.DataFrame()
    
    df = pd.read_csv(file_path, low_memory=False)
    print_progress(f"  Loaded {len(df):,} rows")
    return df


def load_line_score():
    """Load line_score.csv for quarter scores"""
    print_progress("\nLoading line_score.csv...")
    file_path = DATA_DIR / "csv" / "line_score.csv"
    
    if not file_path.exists():
        print_progress("  Warning: line_score.csv not found, skipping...")
        return pd.DataFrame()
    
    df = pd.read_csv(file_path, low_memory=False)
    
    # Convert quarter scores to numeric
    quarter_cols = [col for col in df.columns if 'pts_qtr' in col.lower()]
    for col in quarter_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    print_progress(f"  Loaded {len(df):,} rows")
    return df


def merge_team_statistics(game_df, team_stats_df):
    """Merge detailed team statistics from TeamStatistics.csv"""
    print_progress("\nMerging detailed team statistics...")
    
    if len(team_stats_df) == 0:
        print_progress("  No team statistics to merge")
        return game_df
    
    # Convert gameId to string for consistent merging
    if 'gameId' in team_stats_df.columns:
        team_stats_df['gameId'] = team_stats_df['gameId'].astype(str)
    
    # Create home team stats
    home_stats = team_stats_df[team_stats_df['home'] == 1].copy()
    
    # Rename home team columns
    home_cols_map = {
        'gameId': 'game_id',
        'assists': 'home_assists',
        'blocks': 'home_blocks',
        'steals': 'home_steals',
        'fieldGoalsMade': 'home_fg_made',
        'fieldGoalsAttempted': 'home_fg_attempted',
        'fieldGoalsPercentage': 'home_fg_pct',
        'threePointersMade': 'home_3pt_made',
        'threePointersAttempted': 'home_3pt_attempted',
        'threePointersPercentage': 'home_3pt_pct',
        'freeThrowsMade': 'home_ft_made',
        'freeThrowsAttempted': 'home_ft_attempted',
        'freeThrowsPercentage': 'home_ft_pct',
        'reboundsTotal': 'home_rebounds_total',
        'reboundsOffensive': 'home_rebounds_offensive',
        'reboundsDefensive': 'home_rebounds_defensive',
        'turnovers': 'home_turnovers',
        'foulsPersonal': 'home_fouls',
        'plusMinusPoints': 'home_plus_minus',
        'q1Points': 'home_q1',
        'q2Points': 'home_q2',
        'q3Points': 'home_q3',
        'q4Points': 'home_q4',
        'seasonWins': 'home_season_wins',
        'seasonLosses': 'home_season_losses',
    }
    
    home_cols_map = {k: v for k, v in home_cols_map.items() if k in home_stats.columns}
    home_stats = home_stats.rename(columns=home_cols_map)
    home_merge_cols = ['game_id'] + [v for v in home_cols_map.values() if v != 'game_id']
    
    # Merge home stats (left join - keep all games from game_df)
    print_progress(f"  Attempting to merge {len(home_stats):,} home team stat records...")
    game_df = game_df.merge(
        home_stats[home_merge_cols],
        on='game_id',
        how='left'
    )
    matched = game_df['home_assists'].notna().sum() if 'home_assists' in game_df.columns else 0
    print_progress(f"  Matched {matched:,} games with home team stats ({matched/len(game_df)*100:.1f}%)")
    
    # Create away team stats
    away_stats = team_stats_df[team_stats_df['home'] == 0].copy()
    
    # Rename away team columns
    away_cols_map = {
        'gameId': 'game_id',
        'assists': 'away_assists',
        'blocks': 'away_blocks',
        'steals': 'away_steals',
        'fieldGoalsMade': 'away_fg_made',
        'fieldGoalsAttempted': 'away_fg_attempted',
        'fieldGoalsPercentage': 'away_fg_pct',
        'threePointersMade': 'away_3pt_made',
        'threePointersAttempted': 'away_3pt_attempted',
        'threePointersPercentage': 'away_3pt_pct',
        'freeThrowsMade': 'away_ft_made',
        'freeThrowsAttempted': 'away_ft_attempted',
        'freeThrowsPercentage': 'away_ft_pct',
        'reboundsTotal': 'away_rebounds_total',
        'reboundsOffensive': 'away_rebounds_offensive',
        'reboundsDefensive': 'away_rebounds_defensive',
        'turnovers': 'away_turnovers',
        'foulsPersonal': 'away_fouls',
        'plusMinusPoints': 'away_plus_minus',
        'q1Points': 'away_q1',
        'q2Points': 'away_q2',
        'q3Points': 'away_q3',
        'q4Points': 'away_q4',
        'seasonWins': 'away_season_wins',
        'seasonLosses': 'away_season_losses',
    }
    
    away_cols_map = {k: v for k, v in away_cols_map.items() if k in away_stats.columns}
    away_stats = away_stats.rename(columns=away_cols_map)
    away_merge_cols = ['game_id'] + [v for v in away_cols_map.values() if v != 'game_id']
    
    # Merge away stats (left join)
    print_progress(f"  Attempting to merge {len(away_stats):,} away team stat records...")
    game_df = game_df.merge(
        away_stats[away_merge_cols],
        on='game_id',
        how='left'
    )
    
    merged_count = game_df['home_assists'].notna().sum() if 'home_assists' in game_df.columns else 0
    print_progress(f"  Final: {merged_count:,} games have detailed stats ({merged_count/len(game_df)*100:.1f}%)")
    print_progress(f"  Note: Games without detailed stats will have missing values filled during cleaning")
    
    return game_df


def merge_advanced_stats(game_df, other_stats_df, line_score_df):
    """Merge advanced stats and quarter scores"""
    print_progress("\nMerging advanced stats and quarter scores...")
    
    # Ensure game_id is string in all dataframes for consistent merging
    if 'game_id' in game_df.columns:
        game_df['game_id'] = game_df['game_id'].astype(str)
    
    # Merge other_stats
    if len(other_stats_df) > 0:
        # Create a copy and convert game_id to string
        other_stats_df = other_stats_df.copy()
        if 'game_id' in other_stats_df.columns:
            other_stats_df['game_id'] = other_stats_df['game_id'].astype(str)
        
        other_cols = ['game_id', 'pts_paint_home', 'pts_2nd_chance_home', 'pts_fb_home',
                     'pts_off_to_home', 'pts_paint_away', 'pts_2nd_chance_away',
                     'pts_fb_away', 'pts_off_to_away']
        
        available_cols = [col for col in other_cols if col in other_stats_df.columns]
        if available_cols:
            game_df = game_df.merge(
                other_stats_df[available_cols],
                on='game_id',
                how='left'
            )
            
            rename_map = {
                'pts_paint_home': 'home_points_paint',
                'pts_2nd_chance_home': 'home_points_2nd_chance',
                'pts_fb_home': 'home_points_fast_break',
                'pts_off_to_home': 'home_points_off_turnovers',
                'pts_paint_away': 'away_points_paint',
                'pts_2nd_chance_away': 'away_points_2nd_chance',
                'pts_fb_away': 'away_points_fast_break',
                'pts_off_to_away': 'away_points_off_turnovers'
            }
            game_df = game_df.rename(columns=rename_map)
    
    # Merge line_score for quarter data
    if len(line_score_df) > 0:
        # Convert game_id to string in line_score_df
        line_score_df = line_score_df.copy()
        if 'game_id' in line_score_df.columns:
            line_score_df['game_id'] = line_score_df['game_id'].astype(str)
        
        quarter_cols = ['game_id', 'pts_qtr1_home', 'pts_qtr2_home', 'pts_qtr3_home', 'pts_qtr4_home',
                       'pts_qtr1_away', 'pts_qtr2_away', 'pts_qtr3_away', 'pts_qtr4_away']
        
        available_cols = [col for col in quarter_cols if col in line_score_df.columns]
        if available_cols:
            line_subset = line_score_df[available_cols].copy()
            rename_map = {
                'pts_qtr1_home': 'home_q1',
                'pts_qtr2_home': 'home_q2',
                'pts_qtr3_home': 'home_q3',
                'pts_qtr4_home': 'home_q4',
                'pts_qtr1_away': 'away_q1',
                'pts_qtr2_away': 'away_q2',
                'pts_qtr3_away': 'away_q3',
                'pts_qtr4_away': 'away_q4'
            }
            line_subset = line_subset.rename(columns=rename_map)
            
            # Only update if column doesn't exist or is missing
            for col in ['home_q1', 'home_q2', 'home_q3', 'home_q4', 
                       'away_q1', 'away_q2', 'away_q3', 'away_q4']:
                if col in line_subset.columns:
                    if col not in game_df.columns or game_df[col].isna().sum() > 0:
                        game_df = game_df.merge(
                            line_subset[['game_id', col]],
                            on='game_id',
                            how='left',
                            suffixes=('', '_new')
                        )
                        if f'{col}_new' in game_df.columns:
                            game_df[col] = game_df[col].fillna(game_df[f'{col}_new'])
                            game_df = game_df.drop(columns=[f'{col}_new'])
    
    return game_df


def clean_dataset(df):
    """Clean dataset - less aggressive filtering"""
    print_progress("\nCleaning dataset...")
    
    original_len = len(df)
    
    # Only remove rows with missing critical data (scores and game_id)
    critical_cols = ['game_id', 'game_date', 'home_team_id', 'away_team_id', 
                     'home_score', 'away_score']
    available_critical = [col for col in critical_cols if col in df.columns]
    df = df.dropna(subset=available_critical)
    print_progress(f"  Removed {original_len - len(df):,} rows with missing critical data")
    
    # Remove duplicates
    before_dedup = len(df)
    df = df.drop_duplicates(subset=['game_id'], keep='first')
    print_progress(f"  Removed {before_dedup - len(df):,} duplicate games")
    
    # Remove extreme score outliers (but be less aggressive)
    before_outlier = len(df)
    df = df[(df['home_score'] >= 40) & (df['home_score'] <= 200)]
    df = df[(df['away_score'] >= 40) & (df['away_score'] <= 200)]
    print_progress(f"  Removed {before_outlier - len(df):,} rows with outlier scores")
    
    # Sort by date
    if 'game_date' in df.columns:
        df = df.sort_values('game_date').reset_index(drop=True)
    
    # Fill missing numeric stats (but don't remove rows)
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    excluded_cols = ['game_id', 'home_team_id', 'away_team_id', 'home_team_won', 'season']
    numeric_cols = [col for col in numeric_cols if col not in excluded_cols]
    
    for col in numeric_cols:
        if df[col].isnull().sum() > 0:
            if 'pct' in col.lower():
                df[col] = df[col].fillna(0)
            else:
                median_val = df[col].median()
                df[col] = df[col].fillna(median_val if pd.notna(median_val) else 0)
    
    # Clip percentages
    pct_cols = [col for col in df.columns if 'pct' in col.lower()]
    for col in pct_cols:
        if col in df.columns:
            df[col] = df[col].clip(0, 1)
    
    # Ensure season is integer
    if 'season' in df.columns:
        df['season'] = df['season'].astype('Int64')
    
    print_progress(f"  Final dataset: {len(df):,} rows, {len(df.columns)} columns")
    
    return df


def add_derived_features(df):
    """Add derived features"""
    print_progress("\nAdding derived features...")
    
    features_added = 0
    
    if 'home_score' in df.columns and 'away_score' in df.columns:
        df['point_differential'] = df['home_score'] - df['away_score']
        df['total_points'] = df['home_score'] + df['away_score']
        features_added += 2
    
    if all(col in df.columns for col in ['home_score', 'home_fg_attempted']):
        df['home_offensive_efficiency'] = df['home_score'] / df['home_fg_attempted'].replace(0, np.nan)
        features_added += 1
    
    if all(col in df.columns for col in ['away_score', 'away_fg_attempted']):
        df['away_offensive_efficiency'] = df['away_score'] / df['away_fg_attempted'].replace(0, np.nan)
        features_added += 1
    
    if 'home_rebounds_total' in df.columns and 'away_rebounds_total' in df.columns:
        df['rebound_differential'] = df['home_rebounds_total'] - df['away_rebounds_total']
        features_added += 1
    
    if 'home_turnovers' in df.columns and 'away_turnovers' in df.columns:
        df['turnover_differential'] = df['away_turnovers'] - df['home_turnovers']
        features_added += 1
    
    if 'home_assists' in df.columns and 'home_turnovers' in df.columns:
        df['home_ast_to_to'] = df['home_assists'] / df['home_turnovers'].replace(0, np.nan)
        features_added += 1
    
    if 'away_assists' in df.columns and 'away_turnovers' in df.columns:
        df['away_ast_to_to'] = df['away_assists'] / df['away_turnovers'].replace(0, np.nan)
        features_added += 1
    
    print_progress(f"  Added {features_added} derived features")
    
    return df


def main():
    """Main data preparation pipeline"""
    print_progress("=" * 80)
    print_progress("NBA GAME PREDICTION - DATA PREPARATION (FIXED VERSION)")
    print_progress("=" * 80)
    
    try:
        # Step 1: Load game.csv as primary source
        print_progress("\n[Step 1/6] Loading primary game data...")
        game_df = load_game_data()
        
        # Step 2: Load detailed statistics
        print_progress("\n[Step 2/6] Loading detailed statistics...")
        team_stats_df = load_team_statistics()
        other_stats_df = load_other_stats()
        line_score_df = load_line_score()
        
        # Step 3: Merge detailed stats
        print_progress("\n[Step 3/6] Merging detailed statistics...")
        game_df = merge_team_statistics(game_df, team_stats_df)
        game_df = merge_advanced_stats(game_df, other_stats_df, line_score_df)
        
        # Step 4: Clean data (less aggressive)
        print_progress("\n[Step 4/6] Cleaning dataset...")
        game_df = clean_dataset(game_df)
        
        # Step 5: Add derived features
        print_progress("\n[Step 5/6] Adding derived features...")
        game_df = add_derived_features(game_df)
        
        # Step 6: Save
        print_progress("\n[Step 6/6] Saving final dataset...")
        OUTPUT_DIR.mkdir(exist_ok=True)
        game_df.to_csv(OUTPUT_FILE, index=False)
        
        print_progress(f"\n{'='*80}")
        print_progress("DATA PREPARATION COMPLETE!")
        print_progress(f"{'='*80}")
        print_progress(f"\nFinal dataset saved to: {OUTPUT_FILE}")
        print_progress(f"  - Rows: {len(game_df):,}")
        print_progress(f"  - Columns: {len(game_df.columns)}")
        
        if 'game_date' in game_df.columns:
            print_progress(f"  - Date range: {game_df['game_date'].min()} to {game_df['game_date'].max()}")
        
        if 'season' in game_df.columns:
            print_progress(f"  - Seasons: {game_df['season'].min()} to {game_df['season'].max()}")
            print_progress(f"  - Unique seasons: {game_df['season'].nunique()}")
        
        # Show data completeness
        if 'home_assists' in game_df.columns:
            complete = game_df['home_assists'].notna().sum()
            print_progress(f"  - Games with detailed stats: {complete:,} ({complete/len(game_df)*100:.1f}%)")
        
        return game_df
        
    except Exception as e:
        print_progress(f"\nERROR: {str(e)}")
        import traceback
        print_progress(traceback.format_exc())
        raise


if __name__ == "__main__":
    df = main()

