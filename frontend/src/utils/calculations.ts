import { Player } from "../data/teams";

export interface TeamStats {
  pointsPerGame: number;
  reboundsPerGame: number;
  assistsPerGame: number;
  fieldGoalPercentage: number;
  threePointPercentage: number;
}

export function calculateTeamStatsFromPlayers(players: Player[]): TeamStats {
  if (players.length === 0) {
    return {
      pointsPerGame: 0,
      reboundsPerGame: 0,
      assistsPerGame: 0,
      fieldGoalPercentage: 0,
      threePointPercentage: 0,
    };
  }

  // Calculate averages from selected players
  const totalPoints = players.reduce((sum, player) => sum + player.pointsPerGame, 0);
  const totalRebounds = players.reduce((sum, player) => sum + player.reboundsPerGame, 0);
  const totalAssists = players.reduce((sum, player) => sum + player.assistsPerGame, 0);
  
  // For percentages, calculate weighted average
  const avgFieldGoal = players.reduce((sum, player) => sum + player.fieldGoalPercentage, 0) / players.length;
  const avgThreePoint = players.reduce((sum, player) => sum + player.threePointPercentage, 0) / players.length;

  return {
    pointsPerGame: totalPoints,
    reboundsPerGame: totalRebounds,
    assistsPerGame: totalAssists,
    fieldGoalPercentage: Math.round(avgFieldGoal * 10) / 10,
    threePointPercentage: Math.round(avgThreePoint * 10) / 10,
  };
}

