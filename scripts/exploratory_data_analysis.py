"""
Exploratory Data Analysis (EDA) for NBA Game Prediction Dataset
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
DATA_FILE = PROJECT_ROOT / "data" / "training_dataset.csv"
OUTPUT_DIR = PROJECT_ROOT / "reports"

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

def load_data():
    """Load the training dataset"""
    print("Loading dataset...")
    df = pd.read_csv(DATA_FILE, low_memory=False)
    print(f"Loaded {len(df):,} rows and {len(df.columns)} columns")
    return df

def basic_info(df):
    """Basic dataset information"""
    print("\n" + "="*80)
    print("BASIC DATASET INFORMATION")
    print("="*80)
    
    print(f"\nDataset Shape: {df.shape[0]:,} rows × {df.shape[1]} columns")
    
    # Date range
    if 'game_date' in df.columns:
        df['game_date'] = pd.to_datetime(df['game_date'], errors='coerce')
        print(f"\nDate Range:")
        print(f"  From: {df['game_date'].min()}")
        print(f"  To: {df['game_date'].max()}")
        print(f"  Total days: {(df['game_date'].max() - df['game_date'].min()).days}")
    
    # Seasons
    if 'season' in df.columns:
        print(f"\nSeasons:")
        print(f"  Range: {df['season'].min()} to {df['season'].max()}")
        print(f"  Unique seasons: {df['season'].nunique()}")
        print(f"  Games per season:")
        season_counts = df['season'].value_counts().sort_index()
        for season, count in season_counts.items():
            print(f"    {season}: {count:,} games")
    
    # Missing values
    print(f"\nMissing Values:")
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(2)
    missing_df = pd.DataFrame({
        'Missing Count': missing,
        'Missing %': missing_pct
    })
    missing_df = missing_df[missing_df['Missing Count'] > 0].sort_values('Missing Count', ascending=False)
    if len(missing_df) > 0:
        print(missing_df.head(20).to_string())
        print(f"\n  Total columns with missing values: {len(missing_df)}")
    else:
        print("  No missing values!")
    
    # Data types
    print(f"\nData Types:")
    dtype_counts = df.dtypes.value_counts()
    for dtype, count in dtype_counts.items():
        print(f"  {dtype}: {count} columns")

def target_analysis(df):
    """Analyze the target variable"""
    print("\n" + "="*80)
    print("TARGET VARIABLE ANALYSIS")
    print("="*80)
    
    if 'home_team_won' in df.columns:
        target = df['home_team_won']
        print(f"\nHome Team Win Rate: {target.mean():.2%}")
        print(f"  Home wins: {target.sum():,} ({target.mean():.2%})")
        print(f"  Away wins: {(~target.astype(bool)).sum():,} ({(1-target.mean()):.2%})")
        
        # Win rate by season
        if 'season' in df.columns:
            print(f"\nHome Win Rate by Season:")
            win_rate_by_season = df.groupby('season')['home_team_won'].agg(['mean', 'count'])
            win_rate_by_season.columns = ['Home Win Rate', 'Games']
            for season, row in win_rate_by_season.iterrows():
                print(f"  {season}: {row['Home Win Rate']:.2%} ({int(row['Games']):,} games)")
        
        # Score analysis
        if 'home_score' in df.columns and 'away_score' in df.columns:
            print(f"\nScore Statistics:")
            print(f"  Home team average: {df['home_score'].mean():.2f} points")
            print(f"  Away team average: {df['away_score'].mean():.2f} points")
            print(f"  Home advantage: {df['home_score'].mean() - df['away_score'].mean():.2f} points")
            print(f"  Average total points: {df['home_score'].mean() + df['away_score'].mean():.2f}")

def feature_distributions(df):
    """Analyze feature distributions"""
    print("\n" + "="*80)
    print("FEATURE DISTRIBUTIONS")
    print("="*80)
    
    # Get numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    exclude_cols = ['game_id', 'home_team_id', 'away_team_id', 'season']
    numeric_cols = [col for col in numeric_cols if col not in exclude_cols]
    
    print(f"\nAnalyzing {len(numeric_cols)} numeric features...")
    
    # Key features to analyze
    key_features = [
        'home_score', 'away_score', 'home_fg_pct', 'away_fg_pct',
        'home_3pt_pct', 'away_3pt_pct', 'home_rebounds_total', 'away_rebounds_total',
        'home_assists', 'away_assists', 'home_turnovers', 'away_turnovers',
        'point_differential', 'total_points'
    ]
    
    available_features = [f for f in key_features if f in df.columns]
    
    if available_features:
        print(f"\nKey Feature Statistics:")
        stats = df[available_features].describe()
        print(stats.round(2).to_string())
        
        # Check for outliers
        print(f"\nOutlier Detection (values beyond 3 standard deviations):")
        for col in available_features:
            if df[col].dtype in [np.float64, np.int64]:
                mean = df[col].mean()
                std = df[col].std()
                outliers = ((df[col] - mean).abs() > 3 * std).sum()
                if outliers > 0:
                    print(f"  {col}: {outliers} outliers ({outliers/len(df)*100:.2f}%)")

def correlation_analysis(df):
    """Analyze correlations between features"""
    print("\n" + "="*80)
    print("CORRELATION ANALYSIS")
    print("="*80)
    
    # Select numeric features
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    exclude_cols = ['game_id', 'home_team_id', 'away_team_id', 'season', 'home_team_won']
    feature_cols = [col for col in numeric_cols if col not in exclude_cols]
    
    if len(feature_cols) > 0:
        # Calculate correlations with target
        if 'home_team_won' in df.columns:
            correlations = df[feature_cols + ['home_team_won']].corr()['home_team_won'].sort_values(ascending=False)
            correlations = correlations.drop('home_team_won')
            
            print(f"\nTop 15 Features Correlated with Home Team Win:")
            print(correlations.head(15).to_string())
            print(f"\nBottom 15 Features Correlated with Home Team Win:")
            print(correlations.tail(15).to_string())
            
            # High correlations between features
            print(f"\nHighly Correlated Feature Pairs (|r| > 0.8):")
            corr_matrix = df[feature_cols].corr().abs()
            high_corr_pairs = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    if corr_matrix.iloc[i, j] > 0.8:
                        high_corr_pairs.append((
                            corr_matrix.columns[i],
                            corr_matrix.columns[j],
                            corr_matrix.iloc[i, j]
                        ))
            
            if high_corr_pairs:
                for feat1, feat2, corr in sorted(high_corr_pairs, key=lambda x: x[2], reverse=True)[:10]:
                    print(f"  {feat1} ↔ {feat2}: {corr:.3f}")
            else:
                print("  No highly correlated pairs found")

def team_analysis(df):
    """Analyze team-level statistics"""
    print("\n" + "="*80)
    print("TEAM ANALYSIS")
    print("="*80)
    
    if 'home_team_name' in df.columns:
        # Home win rates by team
        print(f"\nHome Win Rate by Team (Top 15):")
        home_win_rates = df.groupby('home_team_name')['home_team_won'].agg(['mean', 'count'])
        home_win_rates.columns = ['Home Win Rate', 'Home Games']
        home_win_rates = home_win_rates[home_win_rates['Home Games'] >= 50].sort_values('Home Win Rate', ascending=False)
        print(home_win_rates.head(15).to_string())
        
        # Away win rates by team
        if 'away_team_name' in df.columns:
            print(f"\nAway Win Rate by Team (Top 15):")
            away_win_rates = df.groupby('away_team_name')['home_team_won'].apply(lambda x: 1 - x.mean())
            away_win_rates = pd.DataFrame({
                'Away Win Rate': away_win_rates,
                'Away Games': df.groupby('away_team_name').size()
            })
            away_win_rates = away_win_rates[away_win_rates['Away Games'] >= 50].sort_values('Away Win Rate', ascending=False)
            print(away_win_rates.head(15).to_string())

def temporal_analysis(df):
    """Analyze temporal patterns"""
    print("\n" + "="*80)
    print("TEMPORAL ANALYSIS")
    print("="*80)
    
    if 'game_date' in df.columns:
        df['game_date'] = pd.to_datetime(df['game_date'], errors='coerce')
        df['year'] = df['game_date'].dt.year
        df['month'] = df['game_date'].dt.month
        
        # Games by year
        print(f"\nGames by Year:")
        games_by_year = df.groupby('year').size()
        for year, count in games_by_year.items():
            print(f"  {year}: {count:,} games")
        
        # Games by month
        print(f"\nGames by Month:")
        games_by_month = df.groupby('month').size()
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        for month, count in games_by_month.items():
            print(f"  {month_names[month-1]}: {count:,} games")
        
        # Home win rate by month
        if 'home_team_won' in df.columns:
            print(f"\nHome Win Rate by Month:")
            win_rate_by_month = df.groupby('month')['home_team_won'].mean()
            for month, rate in win_rate_by_month.items():
                print(f"  {month_names[month-1]}: {rate:.2%}")

def generate_visualizations(df, output_dir):
    """Generate visualization plots"""
    print("\n" + "="*80)
    print("GENERATING VISUALIZATIONS")
    print("="*80)
    
    output_dir.mkdir(exist_ok=True)
    
    # 1. Score distributions
    if 'home_score' in df.columns and 'away_score' in df.columns:
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        df['home_score'].hist(bins=50, ax=axes[0], alpha=0.7, color='blue')
        axes[0].set_title('Home Team Score Distribution')
        axes[0].set_xlabel('Points')
        axes[0].set_ylabel('Frequency')
        
        df['away_score'].hist(bins=50, ax=axes[1], alpha=0.7, color='red')
        axes[1].set_title('Away Team Score Distribution')
        axes[1].set_xlabel('Points')
        axes[1].set_ylabel('Frequency')
        
        plt.tight_layout()
        plt.savefig(output_dir / 'score_distributions.png', dpi=150, bbox_inches='tight')
        print("  Saved: score_distributions.png")
        plt.close()
    
    # 2. Home win rate by season
    if 'season' in df.columns and 'home_team_won' in df.columns:
        win_rate_by_season = df.groupby('season')['home_team_won'].mean()
        plt.figure(figsize=(12, 6))
        win_rate_by_season.plot(kind='bar', color='steelblue')
        plt.title('Home Team Win Rate by Season')
        plt.xlabel('Season')
        plt.ylabel('Win Rate')
        plt.axhline(y=0.5, color='r', linestyle='--', label='50% Baseline')
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(output_dir / 'home_win_rate_by_season.png', dpi=150, bbox_inches='tight')
        print("  Saved: home_win_rate_by_season.png")
        plt.close()
    
    # 3. Correlation heatmap (top features)
    if 'home_team_won' in df.columns:
        try:
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            exclude_cols = ['game_id', 'home_team_id', 'away_team_id', 'season']
            feature_cols = [col for col in numeric_cols if col not in exclude_cols]
            
            # Select top correlated features
            if len(feature_cols) > 0:
                # Calculate correlation matrix
                corr_matrix = df[feature_cols + ['home_team_won']].corr()
                
                # Get correlations with target - extract as Series directly
                if 'home_team_won' in corr_matrix.columns:
                    target_corrs = corr_matrix['home_team_won'].drop('home_team_won')
                else:
                    # Fallback: calculate correlations manually
                    target_corrs = pd.Series({
                        col: df[col].corr(df['home_team_won']) 
                        for col in feature_cols
                    })
                
                # Ensure it's a Series
                if not isinstance(target_corrs, pd.Series):
                    target_corrs = pd.Series(target_corrs)
                
                # Get absolute values and sort
                correlations = target_corrs.abs().sort_values(ascending=False)
                top_features = correlations.head(20).index.tolist()
                
                if len(top_features) > 1:
                    corr_matrix_top = df[top_features].corr()
                    plt.figure(figsize=(14, 12))
                    sns.heatmap(corr_matrix_top, annot=True, fmt='.2f', cmap='coolwarm', center=0,
                               square=True, linewidths=0.5, cbar_kws={"shrink": 0.8})
                    plt.title('Correlation Heatmap - Top Features')
                    plt.tight_layout()
                    plt.savefig(output_dir / 'correlation_heatmap.png', dpi=150, bbox_inches='tight')
                    print("  Saved: correlation_heatmap.png")
                    plt.close()
        except Exception as e:
            print(f"  Warning: Could not generate correlation heatmap: {e}")
            import traceback
            traceback.print_exc()
    
    # 4. Point differential distribution
    if 'point_differential' in df.columns:
        plt.figure(figsize=(10, 6))
        df['point_differential'].hist(bins=50, alpha=0.7, color='green')
        plt.axvline(x=0, color='r', linestyle='--', linewidth=2, label='Tie')
        plt.title('Point Differential Distribution (Home - Away)')
        plt.xlabel('Point Differential')
        plt.ylabel('Frequency')
        plt.legend()
        plt.tight_layout()
        plt.savefig(output_dir / 'point_differential_distribution.png', dpi=150, bbox_inches='tight')
        print("  Saved: point_differential_distribution.png")
        plt.close()

def main():
    """Main EDA pipeline"""
    print("="*80)
    print("NBA GAME PREDICTION - EXPLORATORY DATA ANALYSIS")
    print("="*80)
    
    # Load data
    df = load_data()
    
    # Run analyses
    basic_info(df)
    target_analysis(df)
    feature_distributions(df)
    correlation_analysis(df)
    team_analysis(df)
    temporal_analysis(df)
    
    # Generate visualizations
    generate_visualizations(df, OUTPUT_DIR)
    
    print("\n" + "="*80)
    print("EDA COMPLETE!")
    print("="*80)
    print(f"\nVisualizations saved to: {OUTPUT_DIR}")
    print(f"\nSummary:")
    print(f"  - Total games: {len(df):,}")
    print(f"  - Date range: {df['game_date'].min()} to {df['game_date'].max()}")
    print(f"  - Home win rate: {df['home_team_won'].mean():.2%}")
    print(f"  - Features: {len(df.columns)}")

if __name__ == "__main__":
    main()

