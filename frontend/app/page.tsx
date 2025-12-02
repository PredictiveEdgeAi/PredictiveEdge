"use client";

import { useState, useEffect } from "react";
import { getPrediction } from "../src/api/predict";
import { getTeams, Team } from "../src/api/teams";
import LoadingScreen from "./loading";
import ThemedSelect from "./components/ThemedSelect";
import styles from "./page.module.css";

export default function HomePage() {
  const [isLoading, setIsLoading] = useState(true);
  const [teams, setTeams] = useState<Team[]>([]);
  const [teamA, setTeamA] = useState<string>("");
  const [teamB, setTeamB] = useState<string>("");
  const [result, setResult] = useState<string | null>(null);
  const [homeWinProbability, setHomeWinProbability] = useState<number | null>(null);
  const [awayWinProbability, setAwayWinProbability] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);

  // Fetch teams from API on component mount
  useEffect(() => {
    const fetchTeams = async () => {
      try {
        const fetchedTeams = await getTeams();
        setTeams(fetchedTeams);
      } catch (error) {
        console.error("Failed to fetch teams:", error);
        // Fallback to empty array if API fails
        setTeams([]);
      }
    };
    fetchTeams();
  }, []);

  const selectedTeamA = teams.find(team => team.id === teamA);
  const selectedTeamB = teams.find(team => team.id === teamB);

  const handleTeamAChange = (value: string) => {
    setTeamA(value);
    setResult(null);
  };

  const handleTeamBChange = (value: string) => {
    setTeamB(value);
    setResult(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedTeamA || !selectedTeamB) {
      alert("Please select both teams");
      return;
    }

    setLoading(true);
    setResult(null);
    setHomeWinProbability(null);
    setAwayWinProbability(null);
    
    try {
      // Use fullName from the API response (e.g., "Los Angeles Lakers")
      const homeTeamName = selectedTeamA.fullName;
      const awayTeamName = selectedTeamB.fullName;
      
      const response = await getPrediction({
        home_team_name: homeTeamName,
        away_team_name: awayTeamName,
      });
      setResult(response.prediction);
      setHomeWinProbability(response.home_win_probability);
      setAwayWinProbability(response.away_win_probability);
    } catch (error) {
      setResult("Error: Could not get analysis. Make sure the backend is running.");
      setHomeWinProbability(null);
      setAwayWinProbability(null);
    } finally {
      setLoading(false);
    }
  };

  const canAnalyze = teamA && teamB;

  return (
    <>
      {/* Loading Screen */}
      {isLoading && (
        <LoadingScreen 
          onLoadingComplete={() => setIsLoading(false)}
          duration={2500}
        />
      )}

      <div className={styles.container}>
        {/* Animated Basketball Court Background */}
        <div className={styles.basketballCourt}>
        <div className={styles.courtLines}></div>
        <div className={styles.courtCircle}></div>
        <div className={styles.courtArc}></div>
        
        {/* Floating Basketballs */}
        <div className={styles.floatingBasketball} style={{ top: '10%', left: '5%', animationDelay: '0s' }}>🏀</div>
        <div className={styles.floatingBasketball} style={{ top: '20%', right: '8%', animationDelay: '1s' }}>🏀</div>
        <div className={styles.floatingBasketball} style={{ bottom: '15%', left: '12%', animationDelay: '2s' }}>🏀</div>
        <div className={styles.floatingBasketball} style={{ bottom: '25%', right: '5%', animationDelay: '1.5s' }}>🏀</div>

        {/* Neon Grid Overlay */}
        <div className={styles.neonGrid}></div>
      </div>

      <div className={styles.content}>
        {/* Header with Animated Logo */}
        <div className={styles.header}>
          <div className={styles.logoContainer}>
            <div className={styles.logoGlow}></div>
            <div className={styles.logo}>🏀</div>
          </div>
          <h1 className={styles.title}>
            <span className={styles.titleGlow}>Predictive</span>
            <span className={styles.titleEdge}>Edge</span>
          </h1>
          <p className={styles.subtitle}>AI-Powered Basketball Analytics Platform</p>
        </div>

        {/* Main Dashboard Card */}
        <div className={styles.dashboardCard}>
          <div className={styles.cardGlow}></div>
          
          <h2 className={styles.cardTitle}>
            <span className={styles.titleIcon}>⚡</span>
            Game Analysis Dashboard
          </h2>
          <p className={styles.cardDescription}>
            Select teams to analyze performance metrics and model estimates
          </p>

          <form onSubmit={handleSubmit} className={styles.form}>
            {/* Team Selection with LED Style */}
            <div className={styles.teamSelection}>
              <div className={styles.teamSelectGroup}>
                <label htmlFor="teamA" className={styles.teamLabel}>
                  <span className={styles.ledLabel}>TEAM A</span>
                </label>
                <ThemedSelect
                  id="teamA"
                  value={teamA}
                  onChange={handleTeamAChange}
                  options={[
                    { value: "", label: "Select Team A" },
                    ...teams.map(team => ({
                      value: team.id,
                      label: `${team.city} ${team.name}`
                    }))
                  ]}
                  placeholder="Select Team A"
                />
              </div>

              <div className={styles.vsDivider}>
                <div className={styles.vsGlow}></div>
                <span>VS</span>
              </div>

              <div className={styles.teamSelectGroup}>
                <label htmlFor="teamB" className={styles.teamLabel}>
                  <span className={styles.ledLabel}>TEAM B</span>
                </label>
                <ThemedSelect
                  id="teamB"
                  value={teamB}
                  onChange={handleTeamBChange}
                  options={[
                    { value: "", label: "Select Team B" },
                    ...teams
                      .filter(team => team.id !== teamA)
                      .map(team => ({
                        value: team.id,
                        label: `${team.city} ${team.name}`
                      }))
                  ]}
                  placeholder="Select Team B"
                  disabled={!teamA}
                />
              </div>
            </div>


            {/* Animated Analyze Button */}
            <button 
              type="submit" 
              className={`${styles.analyzeButton} ${loading ? styles.analyzeButtonLoading : ''}`}
              disabled={loading || !canAnalyze}
            >
              <div className={styles.buttonGlow}></div>
              <span className={styles.buttonText}>
                {loading ? (
                  <>
                    <span className={styles.spinningBall}>🏀</span>
                    Analyzing...
                  </>
                ) : (
                  <>
                    <span className={styles.buttonBasketball}>🏀</span>
                    Analyze Performance
                  </>
                )}
              </span>
            </button>
            
            {!canAnalyze && (
              <p className={styles.helperText}>
                Please select both teams to analyze
              </p>
            )}
          </form>

          {/* Prediction Result with LED Display */}
          {result && (
            <div className={styles.predictionResult}>
              <div className={styles.resultGlow}></div>
              <div className={styles.resultIcon}>
                {result === "1" ? "🏆" : "📉"}
              </div>
              <div className={styles.resultLED}>
                <span className={styles.resultLabel}>MODEL ESTIMATE</span>
                <span className={`${styles.resultValue} ${result === "1" ? styles.resultWin : styles.resultLoss}`}>
                  {result === "1" ? "FAVORED" : "UNDERDOG"}
                </span>
              </div>
              <p className={styles.resultDescription}>
                Based on the {selectedTeamA?.fullName} vs {selectedTeamB?.fullName} matchup, the analytical model estimates Team A ({selectedTeamA?.fullName}) has a{" "}
                <strong>{result === "1" ? "higher probability" : "lower probability"}</strong> of favorable performance based on historical data patterns.
                {result === "1" ? (
                  <span> Team A is predicted to win.</span>
                ) : (
                  <span> Team A is predicted to lose.</span>
                )}
              </p>
              {homeWinProbability !== null && awayWinProbability !== null && (
                <div className={styles.probabilityDisplay}>
                  <div className={styles.probabilityItem}>
                    <span className={styles.probabilityLabel}>Team A (Home) Win Probability:</span>
                    <span className={styles.probabilityValue}>{homeWinProbability}%</span>
                  </div>
                  <div className={styles.probabilityItem}>
                    <span className={styles.probabilityLabel}>Team B (Away) Win Probability:</span>
                    <span className={styles.probabilityValue}>{awayWinProbability}%</span>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
    </>
  );
}
