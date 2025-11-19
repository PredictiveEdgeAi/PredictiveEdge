"use client";

import { useState, useMemo, useEffect } from "react";
import { getPrediction } from "../src/api/predict";
import { teams, Team, Player, getTeamById } from "../src/data/teams";
import { calculateTeamStatsFromPlayers } from "../src/utils/calculations";
import LoadingScreen from "./loading";
import ThemedSelect from "./components/ThemedSelect";
import styles from "./page.module.css";

export default function HomePage() {
  const [isLoading, setIsLoading] = useState(true);
  const [teamA, setTeamA] = useState<string>("");
  const [teamB, setTeamB] = useState<string>("");
  const [teamAPlayers, setTeamAPlayers] = useState<string[]>([]);
  const [teamBPlayers, setTeamBPlayers] = useState<string[]>([]);
  const [result, setResult] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [showStats, setShowStats] = useState(false);
  const [winProbability, setWinProbability] = useState<number | null>(null);

  const selectedTeamA = getTeamById(teamA);
  const selectedTeamB = getTeamById(teamB);

  const teamAStats = useMemo(() => {
    if (!selectedTeamA || teamAPlayers.length === 0) return null;
    const selectedPlayers = selectedTeamA.players.filter(p => teamAPlayers.includes(p.id));
    return calculateTeamStatsFromPlayers(selectedPlayers);
  }, [selectedTeamA, teamAPlayers]);

  const teamBStats = useMemo(() => {
    if (!selectedTeamB || teamBPlayers.length === 0) return null;
    const selectedPlayers = selectedTeamB.players.filter(p => teamBPlayers.includes(p.id));
    return calculateTeamStatsFromPlayers(selectedPlayers);
  }, [selectedTeamB, teamBPlayers]);

  // Calculate win probability based on stats
  useEffect(() => {
    if (teamAStats && teamBStats) {
      const totalPoints = teamAStats.pointsPerGame + teamBStats.pointsPerGame;
      const teamAProb = totalPoints > 0 ? (teamAStats.pointsPerGame / totalPoints) * 100 : 50;
      setWinProbability(Math.round(teamAProb));
    } else {
      setWinProbability(null);
    }
  }, [teamAStats, teamBStats]);

  const handleTeamAChange = (value: string) => {
    setTeamA(value);
    setTeamAPlayers([]);
    setResult(null);
  };

  const handleTeamBChange = (value: string) => {
    setTeamB(value);
    setTeamBPlayers([]);
    setResult(null);
  };

  const toggleTeamAPlayer = (playerId: string) => {
    setTeamAPlayers(prev => 
      prev.includes(playerId) 
        ? prev.filter(id => id !== playerId)
        : [...prev, playerId]
    );
    setResult(null);
  };

  const toggleTeamBPlayer = (playerId: string) => {
    setTeamBPlayers(prev => 
      prev.includes(playerId) 
        ? prev.filter(id => id !== playerId)
        : [...prev, playerId]
    );
    setResult(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!teamAStats || !teamBStats) {
      alert("Please select players for both teams");
      return;
    }

    setLoading(true);
    setResult(null);
    
    try {
      const prediction = await getPrediction({
        teamPointsPerGame: teamAStats.pointsPerGame,
        opponentPointsPerGame: teamBStats.pointsPerGame,
        fieldGoalPercentage: teamAStats.fieldGoalPercentage,
        threePointPercentage: teamAStats.threePointPercentage,
        reboundsPerGame: teamAStats.reboundsPerGame,
        assistsPerGame: teamAStats.assistsPerGame,
      });
      setResult(prediction);
    } catch (error) {
      setResult("Error: Could not get analysis. Make sure the backend is running.");
    } finally {
      setLoading(false);
    }
  };

  const canAnalyze = teamA && teamB && teamAPlayers.length > 0 && teamBPlayers.length > 0;

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

        {/* LED Scoreboard Panel */}
        {winProbability !== null && (
          <div className={styles.ledScoreboard}>
            <div className={styles.ledPanel}>
              <div className={styles.ledHeader}>
                <span className={styles.ledText}>WIN PROBABILITY</span>
              </div>
              <div className={styles.ledDisplay}>
                <div className={styles.probabilityContainer}>
                  <div className={styles.probabilityBar}>
                    <div 
                      className={styles.probabilityFill} 
                      style={{ width: `${winProbability}%` }}
                    >
                      <span className={styles.probabilityText}>{winProbability}%</span>
                    </div>
                  </div>
                  <div className={styles.teamLabels}>
                    <span className={styles.teamLabel}>{selectedTeamA?.abbreviation || 'TEAM A'}</span>
                    <span className={styles.teamLabel}>{selectedTeamB?.abbreviation || 'TEAM B'}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Main Dashboard Card */}
        <div className={styles.dashboardCard}>
          <div className={styles.cardGlow}></div>
          
          <h2 className={styles.cardTitle}>
            <span className={styles.titleIcon}>⚡</span>
            Game Analysis Dashboard
          </h2>
          <p className={styles.cardDescription}>
            Select teams and players to analyze performance metrics and model estimates
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

            {/* Player Selection with Animated Cards */}
            {(selectedTeamA || selectedTeamB) && (
              <div className={styles.playerSelection}>
                {selectedTeamA && (
                  <div className={styles.playerGroup}>
                    <div className={styles.playerGroupGlow}></div>
                    <h3 className={styles.playerGroupTitle}>
                      <span className={styles.teamIcon}>🏀</span>
                      {selectedTeamA.city} {selectedTeamA.name}
                    </h3>
                    <div className={styles.playerList}>
                      {selectedTeamA.players.map(player => (
                        <label 
                          key={player.id} 
                          className={`${styles.playerCard} ${teamAPlayers.includes(player.id) ? styles.playerCardSelected : ''}`}
                        >
                          <input
                            type="checkbox"
                            checked={teamAPlayers.includes(player.id)}
                            onChange={() => toggleTeamAPlayer(player.id)}
                            className={styles.playerCheckbox}
                          />
                          <div className={styles.playerInfo}>
                            <span className={styles.playerName}>{player.name}</span>
                            <span className={styles.playerPosition}>{player.position}</span>
                          </div>
                          <div className={styles.playerStatsMini}>
                            <span className={styles.statValue}>{player.pointsPerGame}</span>
                            <span className={styles.statLabel}>PPG</span>
                          </div>
                          <div className={styles.playerCardGlow}></div>
                        </label>
                      ))}
                    </div>
                  </div>
                )}

                {selectedTeamB && (
                  <div className={styles.playerGroup}>
                    <div className={styles.playerGroupGlow}></div>
                    <h3 className={styles.playerGroupTitle}>
                      <span className={styles.teamIcon}>🏀</span>
                      {selectedTeamB.city} {selectedTeamB.name}
                    </h3>
                    <div className={styles.playerList}>
                      {selectedTeamB.players.map(player => (
                        <label 
                          key={player.id} 
                          className={`${styles.playerCard} ${teamBPlayers.includes(player.id) ? styles.playerCardSelected : ''}`}
                        >
                          <input
                            type="checkbox"
                            checked={teamBPlayers.includes(player.id)}
                            onChange={() => toggleTeamBPlayer(player.id)}
                            className={styles.playerCheckbox}
                          />
                          <div className={styles.playerInfo}>
                            <span className={styles.playerName}>{player.name}</span>
                            <span className={styles.playerPosition}>{player.position}</span>
                          </div>
                          <div className={styles.playerStatsMini}>
                            <span className={styles.statValue}>{player.pointsPerGame}</span>
                            <span className={styles.statLabel}>PPG</span>
                          </div>
                          <div className={styles.playerCardGlow}></div>
                        </label>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Interactive Stats Preview with Animated Graphs */}
            {(teamAStats || teamBStats) && (
              <div className={styles.statsPreview}>
                <button
                  type="button"
                  onClick={() => setShowStats(!showStats)}
                  className={styles.showStatsButton}
                >
                  <span className={styles.buttonIcon}>{showStats ? '▼' : '▶'}</span>
                  {showStats ? "Hide" : "Show"} Calculated Statistics
                </button>
                {showStats && (
                  <div className={styles.statsGrid}>
                    {teamAStats && (
                      <div className={styles.statsCard}>
                        <div className={styles.statsCardGlow}></div>
                        <h4>{selectedTeamA?.city} {selectedTeamA?.name}</h4>
                        <div className={styles.statRow}>
                          <span>Points/Game</span>
                          <div className={styles.statBarContainer}>
                            <div 
                              className={styles.statBarFill} 
                              style={{ width: `${(teamAStats.pointsPerGame / 150) * 100}%` }}
                            >
                              <strong>{teamAStats.pointsPerGame.toFixed(1)}</strong>
                            </div>
                          </div>
                        </div>
                        <div className={styles.statRow}>
                          <span>Rebounds</span>
                          <div className={styles.statBarContainer}>
                            <div 
                              className={styles.statBarFill} 
                              style={{ width: `${(teamAStats.reboundsPerGame / 60) * 100}%` }}
                            >
                              <strong>{teamAStats.reboundsPerGame.toFixed(1)}</strong>
                            </div>
                          </div>
                        </div>
                        <div className={styles.statRow}>
                          <span>Assists</span>
                          <div className={styles.statBarContainer}>
                            <div 
                              className={styles.statBarFill} 
                              style={{ width: `${(teamAStats.assistsPerGame / 40) * 100}%` }}
                            >
                              <strong>{teamAStats.assistsPerGame.toFixed(1)}</strong>
                            </div>
                          </div>
                        </div>
                        <div className={styles.statRow}>
                          <span>FG%</span>
                          <strong className={styles.percentageValue}>{teamAStats.fieldGoalPercentage}%</strong>
                        </div>
                        <div className={styles.statRow}>
                          <span>3PT%</span>
                          <strong className={styles.percentageValue}>{teamAStats.threePointPercentage}%</strong>
                        </div>
                      </div>
                    )}
                    {teamBStats && (
                      <div className={styles.statsCard}>
                        <div className={styles.statsCardGlow}></div>
                        <h4>{selectedTeamB?.city} {selectedTeamB?.name}</h4>
                        <div className={styles.statRow}>
                          <span>Points/Game</span>
                          <div className={styles.statBarContainer}>
                            <div 
                              className={styles.statBarFill} 
                              style={{ width: `${(teamBStats.pointsPerGame / 150) * 100}%` }}
                            >
                              <strong>{teamBStats.pointsPerGame.toFixed(1)}</strong>
                            </div>
                          </div>
                        </div>
                        <div className={styles.statRow}>
                          <span>Rebounds</span>
                          <div className={styles.statBarContainer}>
                            <div 
                              className={styles.statBarFill} 
                              style={{ width: `${(teamBStats.reboundsPerGame / 60) * 100}%` }}
                            >
                              <strong>{teamBStats.reboundsPerGame.toFixed(1)}</strong>
                            </div>
                          </div>
                        </div>
                        <div className={styles.statRow}>
                          <span>Assists</span>
                          <div className={styles.statBarContainer}>
                            <div 
                              className={styles.statBarFill} 
                              style={{ width: `${(teamBStats.assistsPerGame / 40) * 100}%` }}
                            >
                              <strong>{teamBStats.assistsPerGame.toFixed(1)}</strong>
                            </div>
                          </div>
                        </div>
                        <div className={styles.statRow}>
                          <span>FG%</span>
                          <strong className={styles.percentageValue}>{teamBStats.fieldGoalPercentage}%</strong>
                        </div>
                        <div className={styles.statRow}>
                          <span>3PT%</span>
                          <strong className={styles.percentageValue}>{teamBStats.threePointPercentage}%</strong>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}

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
            
            {!canAnalyze && teamA && teamB && (
              <p className={styles.helperText}>
                Please select at least one player from each team to analyze
              </p>
            )}
          </form>

          {/* Prediction Result with LED Display */}
          {result && (
            <div className={styles.predictionResult}>
              <div className={styles.resultGlow}></div>
              <div className={styles.resultIcon}>
                {result === "Win" || result === "1" ? "🏆" : "📉"}
              </div>
              <div className={styles.resultLED}>
                <span className={styles.resultLabel}>MODEL ESTIMATE</span>
                <span className={`${styles.resultValue} ${result === "Win" || result === "1" ? styles.resultWin : styles.resultLoss}`}>
                  {result === "Win" || result === "1" ? "FAVORED" : "UNDERDOG"}
                </span>
              </div>
              <p className={styles.resultDescription}>
                Based on the selected {selectedTeamA?.name} lineup, the analytical model estimates Team A has a{" "}
                <strong>{result === "Win" || result === "1" ? "higher probability" : "lower probability"}</strong> of favorable performance against {selectedTeamB?.name} based on historical data patterns.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
    </>
  );
}
