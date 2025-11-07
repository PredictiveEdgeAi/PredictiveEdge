"use client";

import { useState } from "react";
import { getPrediction } from "../src/api/predict";
import styles from "./page.module.css";

export default function HomePage() {
  const [input, setInput] = useState({ 
    teamPointsPerGame: "", 
    opponentPointsPerGame: "",
    fieldGoalPercentage: "",
    threePointPercentage: "",
    reboundsPerGame: "",
    assistsPerGame: ""
  });
  const [result, setResult] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInput({ ...input, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    
    try {
      const prediction = await getPrediction({
        teamPointsPerGame: parseFloat(input.teamPointsPerGame),
        opponentPointsPerGame: parseFloat(input.opponentPointsPerGame),
        fieldGoalPercentage: parseFloat(input.fieldGoalPercentage),
        threePointPercentage: parseFloat(input.threePointPercentage),
        reboundsPerGame: parseFloat(input.reboundsPerGame),
        assistsPerGame: parseFloat(input.assistsPerGame),
      });
      setResult(prediction);
    } catch (error) {
      setResult("Error: Could not get analysis. Make sure the backend is running.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.basketballCourt}>
        <div className={styles.content}>
          <div className={styles.header}>
            <div className={styles.logo}>🏀</div>
            <h1 className={styles.title}>PredictiveEdge</h1>
            <p className={styles.subtitle}>AI-Powered Basketball Analytics Platform</p>
          </div>

          <div className={styles.card}>
            <h2 className={styles.cardTitle}>Performance Analysis</h2>
            <p className={styles.cardDescription}>
              Enter team statistics to analyze performance metrics and model estimates
            </p>

            <form onSubmit={handleSubmit} className={styles.form}>
              <div className={styles.formGrid}>
                <div className={styles.inputGroup}>
                  <label htmlFor="teamPointsPerGame">Team Points/Game</label>
                  <input
                    id="teamPointsPerGame"
                    name="teamPointsPerGame"
                    type="number"
                    step="0.1"
                    placeholder="e.g., 110.5"
                    value={input.teamPointsPerGame}
                    onChange={handleChange}
                    required
                  />
                </div>

                <div className={styles.inputGroup}>
                  <label htmlFor="opponentPointsPerGame">Opponent Points/Game</label>
                  <input
                    id="opponentPointsPerGame"
                    name="opponentPointsPerGame"
                    type="number"
                    step="0.1"
                    placeholder="e.g., 108.2"
                    value={input.opponentPointsPerGame}
                    onChange={handleChange}
                    required
                  />
                </div>

                <div className={styles.inputGroup}>
                  <label htmlFor="fieldGoalPercentage">Field Goal %</label>
                  <input
                    id="fieldGoalPercentage"
                    name="fieldGoalPercentage"
                    type="number"
                    step="0.1"
                    placeholder="e.g., 45.8"
                    value={input.fieldGoalPercentage}
                    onChange={handleChange}
                    required
                  />
                </div>

                <div className={styles.inputGroup}>
                  <label htmlFor="threePointPercentage">3-Point %</label>
                  <input
                    id="threePointPercentage"
                    name="threePointPercentage"
                    type="number"
                    step="0.1"
                    placeholder="e.g., 36.5"
                    value={input.threePointPercentage}
                    onChange={handleChange}
                    required
                  />
                </div>

                <div className={styles.inputGroup}>
                  <label htmlFor="reboundsPerGame">Rebounds/Game</label>
                  <input
                    id="reboundsPerGame"
                    name="reboundsPerGame"
                    type="number"
                    step="0.1"
                    placeholder="e.g., 44.2"
                    value={input.reboundsPerGame}
                    onChange={handleChange}
                    required
                  />
                </div>

                <div className={styles.inputGroup}>
                  <label htmlFor="assistsPerGame">Assists/Game</label>
                  <input
                    id="assistsPerGame"
                    name="assistsPerGame"
                    type="number"
                    step="0.1"
                    placeholder="e.g., 24.8"
                    value={input.assistsPerGame}
                    onChange={handleChange}
                    required
                  />
                </div>
              </div>

              <button 
                type="submit" 
                className={styles.predictButton}
                disabled={loading}
              >
                {loading ? "Analyzing..." : "🏀 Analyze Performance"}
              </button>
            </form>

            {result && (
              <div className={styles.result}>
                <div className={styles.resultIcon}>
                  {result === "Win" || result === "1" ? "📊" : "📉"}
                </div>
                <h3 className={styles.resultTitle}>
                  Model Estimate: <span className={styles.resultValue}>
                    {result === "Win" || result === "1" ? "FAVORED" : "UNDERDOG"}
                  </span>
                </h3>
                <p className={styles.resultDescription}>
                  Based on the provided statistics, the analytical model estimates this team has a{" "}
                  <strong>{result === "Win" || result === "1" ? "higher probability" : "lower probability"}</strong> of favorable performance based on historical data patterns.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
