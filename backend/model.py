# model.py — Basketball prediction model
# Replace this with your real trained model
from sklearn.linear_model import LogisticRegression
import numpy as np

# Initialize and train a sample model with basketball-like data
# Features: [team_ppg, opponent_ppg, fg%, 3pt%, rebounds, assists]
model = LogisticRegression()

# Sample training data (6 features per sample)
# Higher team PPG, FG%, 3PT%, rebounds, assists = more likely to win
# Lower opponent PPG = more likely to win
training_data = [
    # Wins (label 1)
    [115.5, 108.2, 47.5, 38.2, 45.5, 26.8],  # Strong team
    [112.3, 110.1, 46.2, 36.8, 44.2, 25.3],  # Good team
    [110.8, 111.5, 45.8, 35.5, 43.8, 24.5],  # Average team winning
    [118.2, 105.3, 48.5, 39.5, 47.2, 28.5],  # Elite team
    [109.5, 112.8, 44.5, 34.2, 42.5, 23.8],  # Slight edge
    # Losses (label 0)
    [105.2, 115.8, 43.2, 33.5, 40.2, 22.3],  # Weak team
    [108.5, 112.3, 44.8, 35.2, 41.8, 23.5],  # Below average
    [107.8, 114.5, 43.5, 32.8, 39.5, 21.8],  # Poor team
    [103.5, 118.2, 42.2, 31.5, 38.2, 20.5],  # Very weak
    [106.2, 113.5, 44.2, 34.5, 40.8, 22.8],  # Losing team
]

labels = [1, 1, 1, 1, 1, 0, 0, 0, 0, 0]

model.fit(training_data, labels)

def predict_outcome(features):
    """
    Predict basketball game outcome based on team statistics.
    
    Args:
        features: List of 6 features [team_ppg, opponent_ppg, fg%, 3pt%, rebounds, assists]
    
    Returns:
        1 for Win, 0 for Loss
    """
    prediction = model.predict([features])[0]
    return prediction
