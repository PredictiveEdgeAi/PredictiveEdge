"""
Simple EDA for NBA Game Prediction Dataset (Text Output Only)
"""
import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
DATA_FILE = PROJECT_ROOT / "data" / "training_dataset.csv"
OUTPUT_FILE = PROJECT_ROOT / "reports" / "eda_report.txt"

def main():
    """Main EDA pipeline"""
    print("="*80)
    print("NBA GAME PREDICTION - EXPLORATORY DATA ANALYSIS")
    print("="*80)
    
    # Load data
    print("\nLoading dataset...")
    df = pd.read_csv(DATA_FILE, low_memory=False)
    print(f"Loaded {len(df):,} rows and {len(df.columns)} columns")
    
    # Convert date
    if 'game_date' in df.columns:
        df['game_date'] = pd.to_datetime(df['game_date'], errors='coerce')
    
    # Open output file
    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        def write(msg):
            print(msg)
            f.write(str(msg) + '\n')
        
        write("\n" + "="*80)
        write("BASIC DATASET INFORMATION")
        write("="*80)
        write(f"\nDataset Shape: {df.shape[0]:,} rows × {df.shape[1]} columns")
        
        # Date range
        if 'game_date' in df.columns:
            write(f"\nDate Range:")
            write(f"  From: {df['game_date'].min()}")
            write(f"  To: {df['game_date'].max()}")
            write(f"  Total days: {(df['game_date'].max() - df['game_date'].min()).days}")
        
        # Seasons
        if 'season' in df.columns:
            write(f"\nSeasons:")
            write(f"  Range: {df['season'].min()} to {df['season'].max()}")
            write(f"  Unique seasons: {df['season'].nunique()}")
            write(f"  Games per season:")
            season_counts = df['season'].value_counts().sort_index()
            for season, count in season_counts.head(20).items():
                write(f"    {season}: {count:,} games")
        
        # Missing values
        write(f"\nMissing Values (Top 20):")
        missing = df.isnull().sum()
        missing_pct = (missing / len(df) * 100).round(2)
        missing_df = pd.DataFrame({
            'Missing Count': missing,
            'Missing %': missing_pct
        })
        missing_df = missing_df[missing_df['Missing Count'] > 0].sort_values('Missing Count', ascending=False)
        if len(missing_df) > 0:
            write(missing_df.head(20).to_string())
        else:
            write("  No missing values!")
        
        # Target analysis
        write("\n" + "="*80)
        write("TARGET VARIABLE ANALYSIS")
        write("="*80)
        
        if 'home_team_won' in df.columns:
            target = df['home_team_won']
            write(f"\nHome Team Win Rate: {target.mean():.2%}")
            write(f"  Home wins: {target.sum():,} ({target.mean():.2%})")
            write(f"  Away wins: {(~target.astype(bool)).sum():,} ({(1-target.mean()):.2%})")
            
            # Score analysis
            if 'home_score' in df.columns and 'away_score' in df.columns:
                write(f"\nScore Statistics:")
                write(f"  Home team average: {df['home_score'].mean():.2f} points")
                write(f"  Away team average: {df['away_score'].mean():.2f} points")
                write(f"  Home advantage: {df['home_score'].mean() - df['away_score'].mean():.2f} points")
                write(f"  Average total points: {df['home_score'].mean() + df['away_score'].mean():.2f}")
        
        # Feature correlations
        write("\n" + "="*80)
        write("FEATURE CORRELATIONS WITH TARGET")
        write("="*80)
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        exclude_cols = ['game_id', 'home_team_id', 'away_team_id', 'season', 'home_team_won']
        feature_cols = [col for col in numeric_cols if col not in exclude_cols]
        
        if 'home_team_won' in df.columns and len(feature_cols) > 0:
            correlations = df[feature_cols + ['home_team_won']].corr()['home_team_won'].sort_values(ascending=False)
            correlations = correlations.drop('home_team_won')
            
            write(f"\nTop 20 Features Correlated with Home Team Win:")
            for feat, corr in correlations.head(20).items():
                write(f"  {feat:40s}: {corr:7.4f}")
            
            write(f"\nBottom 20 Features Correlated with Home Team Win:")
            for feat, corr in correlations.tail(20).items():
                write(f"  {feat:40s}: {corr:7.4f}")
        
        # Key statistics
        write("\n" + "="*80)
        write("KEY FEATURE STATISTICS")
        write("="*80)
        
        key_features = [
            'home_score', 'away_score', 'home_fg_pct', 'away_fg_pct',
            'home_3pt_pct', 'away_3pt_pct', 'home_rebounds_total', 'away_rebounds_total',
            'home_assists', 'away_assists', 'home_turnovers', 'away_turnovers',
            'point_differential', 'total_points'
        ]
        
        available_features = [f for f in key_features if f in df.columns]
        if available_features:
            write("\n" + df[available_features].describe().to_string())
        
        write("\n" + "="*80)
        write("EDA COMPLETE!")
        write("="*80)
        write(f"\nReport saved to: {OUTPUT_FILE}")
    
    print(f"\nEDA report saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()

