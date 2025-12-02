# Exploratory Data Analysis (EDA) Summary

## 📊 Dataset Overview

- **Total Games**: 65,638 games
- **Date Range**: November 1, 1946 to June 12, 2023 (27,982 days)
- **Seasons**: 77 unique seasons (1946-2022)
- **Features**: 121 columns
- **Data Quality**: Excellent - only 6 columns with missing values (<0.1%)

## 🎯 Key Findings

### 1. Home Court Advantage
- **Home Win Rate**: 61.89% (40,623 wins vs 25,015 losses)
- **Home Advantage**: 3.63 points on average
  - Home team average: 104.60 points
  - Away team average: 100.97 points
- **Temporal Trend**: Home advantage has decreased over time
  - 1950s-1960s: ~70-76% home win rate
  - 2010s-2020s: ~54-58% home win rate

### 2. Top Predictive Features

**Highest Correlations with Home Team Win:**
1. `point_differential`: 0.791 (Home score - Away score)
2. `plus_minus_home`: 0.791
3. `home_plus_minus`: 0.777
4. `home_offensive_efficiency`: 0.395
5. `home_score`: 0.362
6. `rebound_differential`: 0.304
7. `home_fg_made`: 0.299
8. `home_assists`: 0.274
9. `home_rebounds_defensive`: 0.257
10. `home_ast_to_to`: 0.187

**Key Insight**: Point differential is by far the strongest predictor, which makes sense as it directly reflects the game outcome.

### 3. Feature Statistics

**Scoring:**
- Average total points per game: 205.57
- Home team: 104.60 ± 14.72 points
- Away team: 100.97 ± 14.37 points

**Shooting Percentages:**
- Field goal %: ~36% (home) vs ~35% (away)
- 3-point %: ~24% for both teams
- Free throw %: Not shown but typically ~75-80%

**Other Stats:**
- Rebounds: 43.56 (home) vs 42.07 (away)
- Assists: 23.94 (home) vs 22.09 (away)
- Turnovers: 14.83 (home) vs 15.13 (away)

### 4. Outlier Detection

Very few outliers detected (<1% for most features):
- Home score: 312 outliers (0.48%)
- Away score: 275 outliers (0.42%)
- Turnovers: 794 outliers (1.21%) - highest
- Most features have <1% outliers, indicating clean data

### 5. Team Performance

**Best Home Teams (Historical):**
1. Syracuse Nationals: 79.6% (495 games)
2. Minneapolis Lakers: 78.5% (460 games)
3. St. Louis Hawks: 77.4% (429 games)
4. San Antonio Spurs: 71.0% (2,040 games) - modern team
5. Boston Celtics: 70.4% (3,122 games) - modern team

**Best Away Teams:**
1. LA Clippers: 52.0% (354 games)
2. Los Angeles Lakers: 50.1% (2,542 games)
3. San Antonio Spurs: 48.1% (2,037 games)

### 6. Temporal Patterns

**Games by Month:**
- Peak: March (11,267 games), January (11,225 games)
- Low: September (40 games), July (16 games)
- Regular season: Oct-Apr
- Playoffs: May-June

**Home Win Rate by Month:**
- Highest: May (63.55%) - Playoffs
- Lowest: September (40.00%) - Preseason
- Regular season: ~60-62%

### 7. Highly Correlated Features

**Perfect Correlations (r = 1.0):**
- `plus_minus_home` ↔ `point_differential`
- `plus_minus_home` ↔ `plus_minus_away` (inverse relationship)
- `video_available_home` ↔ `video_available_away`

**Very High Correlations (r > 0.99):**
- `blk_home` ↔ `home_blocks`
- `dreb_home` ↔ `home_rebounds_defensive`
- `fg3m_home` ↔ `home_3pt_made`

**Recommendation**: Remove duplicate/redundant features to reduce multicollinearity.

## 📈 Data Quality Assessment

### Strengths:
✅ **Comprehensive Coverage**: 77 seasons of data (1946-2022)
✅ **High Completeness**: Only 6 columns with missing values
✅ **Clean Data**: Minimal outliers (<1% for most features)
✅ **Rich Features**: 121 columns with detailed statistics
✅ **Balanced**: Good representation across seasons and teams

### Areas for Improvement:
⚠️ **Feature Redundancy**: Many duplicate features (e.g., `plus_minus_home` vs `point_differential`)
⚠️ **Missing Advanced Features**: No rolling averages, H2H records, or rest days yet
⚠️ **Season Imbalance**: Some seasons have very few games (e.g., 1960: 1 game, 1961: 30 games)

## 🎯 Recommendations for Model Training

1. **Feature Selection**:
   - Remove redundant features (keep one of each highly correlated pair)
   - Focus on: point differential, offensive efficiency, rebounds, assists
   - Add advanced features: rolling averages, H2H, rest days

2. **Data Splitting**:
   - Use temporal split (train on older seasons, test on recent)
   - Consider: Train 1946-2015, Validate 2016-2019, Test 2020-2022

3. **Target Variable**:
   - Primary: `home_team_won` (binary classification)
   - Secondary: `point_differential` (regression for margin prediction)

4. **Feature Engineering Needed**:
   - ✅ Basic derived features (done)
   - ❌ Rolling averages (last 5/10 games) - **TODO**
   - ❌ Head-to-head records - **TODO**
   - ❌ Rest days calculation - **TODO**
   - ❌ Recent form metrics - **TODO**

## 📊 Visualizations Generated

1. ✅ `score_distributions.png` - Home vs Away score distributions
2. ✅ `home_win_rate_by_season.png` - Home advantage trend over time
3. ⚠️ `correlation_heatmap.png` - (Fixed, should generate on next run)
4. ⚠️ `point_differential_distribution.png` - (Should generate on next run)

## 🔍 Next Steps

1. **Add Advanced Feature Engineering**:
   - Implement rolling averages calculation
   - Calculate head-to-head win percentages
   - Add rest days feature
   - Create recent form metrics

2. **Feature Selection**:
   - Remove redundant features
   - Select top 30-50 most predictive features

3. **Model Training**:
   - Temporal train/validation/test split
   - Train multiple models (Logistic Regression, Random Forest, XGBoost, LightGBM)
   - Evaluate and select best model

---

**Generated**: From EDA run on training dataset
**Dataset**: `data/training_dataset.csv` (65,638 games, 121 features)

