export interface Player {
  id: string;
  name: string;
  position: string;
  pointsPerGame: number;
  reboundsPerGame: number;
  assistsPerGame: number;
  fieldGoalPercentage: number;
  threePointPercentage: number;
}

export interface Team {
  id: string;
  name: string;
  city: string;
  abbreviation: string;
  players: Player[];
  teamPointsPerGame: number;
  teamReboundsPerGame: number;
  teamAssistsPerGame: number;
  teamFieldGoalPercentage: number;
  teamThreePointPercentage: number;
}

export const teams: Team[] = [
  {
    id: "lakers",
    name: "Lakers",
    city: "Los Angeles",
    abbreviation: "LAL",
    teamPointsPerGame: 112.5,
    teamReboundsPerGame: 44.2,
    teamAssistsPerGame: 25.8,
    teamFieldGoalPercentage: 47.5,
    teamThreePointPercentage: 36.8,
    players: [
      { id: "lebron", name: "LeBron James", position: "SF", pointsPerGame: 25.2, reboundsPerGame: 7.8, assistsPerGame: 7.5, fieldGoalPercentage: 52.0, threePointPercentage: 35.2 },
      { id: "davis", name: "Anthony Davis", position: "PF/C", pointsPerGame: 24.8, reboundsPerGame: 12.5, assistsPerGame: 3.2, fieldGoalPercentage: 55.8, threePointPercentage: 28.5 },
      { id: "russell", name: "D'Angelo Russell", position: "PG", pointsPerGame: 18.5, reboundsPerGame: 3.2, assistsPerGame: 6.8, fieldGoalPercentage: 45.5, threePointPercentage: 38.5 },
      { id: "reaves", name: "Austin Reaves", position: "SG", pointsPerGame: 15.8, reboundsPerGame: 4.2, assistsPerGame: 5.2, fieldGoalPercentage: 48.2, threePointPercentage: 37.8 },
      { id: "hachimura", name: "Rui Hachimura", position: "PF", pointsPerGame: 13.5, reboundsPerGame: 4.8, assistsPerGame: 1.8, fieldGoalPercentage: 52.5, threePointPercentage: 39.2 },
    ]
  },
  {
    id: "warriors",
    name: "Warriors",
    city: "Golden State",
    abbreviation: "GSW",
    teamPointsPerGame: 118.2,
    teamReboundsPerGame: 45.8,
    teamAssistsPerGame: 29.5,
    teamFieldGoalPercentage: 48.2,
    teamThreePointPercentage: 38.5,
    players: [
      { id: "curry", name: "Stephen Curry", position: "PG", pointsPerGame: 26.8, reboundsPerGame: 4.5, assistsPerGame: 5.2, fieldGoalPercentage: 46.5, threePointPercentage: 40.8 },
      { id: "thompson", name: "Klay Thompson", position: "SG", pointsPerGame: 17.8, reboundsPerGame: 3.5, assistsPerGame: 2.2, fieldGoalPercentage: 43.5, threePointPercentage: 38.2 },
      { id: "green", name: "Draymond Green", position: "PF/C", pointsPerGame: 8.5, reboundsPerGame: 7.2, assistsPerGame: 6.8, fieldGoalPercentage: 49.5, threePointPercentage: 32.5 },
      { id: "wiggins", name: "Andrew Wiggins", position: "SF", pointsPerGame: 13.2, reboundsPerGame: 4.8, assistsPerGame: 2.5, fieldGoalPercentage: 45.8, threePointPercentage: 35.8 },
      { id: "kuminga", name: "Jonathan Kuminga", position: "SF/PF", pointsPerGame: 16.2, reboundsPerGame: 4.8, assistsPerGame: 2.2, fieldGoalPercentage: 52.5, threePointPercentage: 32.2 },
    ]
  },
  {
    id: "celtics",
    name: "Celtics",
    city: "Boston",
    abbreviation: "BOS",
    teamPointsPerGame: 120.8,
    teamReboundsPerGame: 47.2,
    teamAssistsPerGame: 26.8,
    teamFieldGoalPercentage: 48.8,
    teamThreePointPercentage: 39.5,
    players: [
      { id: "tatum", name: "Jayson Tatum", position: "SF", pointsPerGame: 27.2, reboundsPerGame: 8.2, assistsPerGame: 4.8, fieldGoalPercentage: 47.5, threePointPercentage: 37.5 },
      { id: "brown", name: "Jaylen Brown", position: "SG/SF", pointsPerGame: 23.5, reboundsPerGame: 5.8, assistsPerGame: 3.5, fieldGoalPercentage: 49.8, threePointPercentage: 36.8 },
      { id: "white", name: "Derrick White", position: "PG/SG", pointsPerGame: 15.2, reboundsPerGame: 4.2, assistsPerGame: 5.2, fieldGoalPercentage: 46.2, threePointPercentage: 39.5 },
      { id: "porzingis", name: "Kristaps Porzingis", position: "C", pointsPerGame: 20.5, reboundsPerGame: 7.8, assistsPerGame: 2.2, fieldGoalPercentage: 51.5, threePointPercentage: 37.8 },
      { id: "holiday", name: "Jrue Holiday", position: "PG", pointsPerGame: 12.8, reboundsPerGame: 5.2, assistsPerGame: 5.5, fieldGoalPercentage: 48.2, threePointPercentage: 42.5 },
    ]
  },
  {
    id: "nuggets",
    name: "Nuggets",
    city: "Denver",
    abbreviation: "DEN",
    teamPointsPerGame: 114.5,
    teamReboundsPerGame: 44.5,
    teamAssistsPerGame: 28.8,
    teamFieldGoalPercentage: 49.2,
    teamThreePointPercentage: 37.5,
    players: [
      { id: "jokic", name: "Nikola Jokic", position: "C", pointsPerGame: 26.8, reboundsPerGame: 12.5, assistsPerGame: 9.2, fieldGoalPercentage: 58.5, threePointPercentage: 35.2 },
      { id: "murray", name: "Jamal Murray", position: "PG", pointsPerGame: 21.2, reboundsPerGame: 4.2, assistsPerGame: 6.5, fieldGoalPercentage: 48.5, threePointPercentage: 42.2 },
      { id: "porter", name: "Michael Porter Jr.", position: "SF", pointsPerGame: 16.8, reboundsPerGame: 7.2, assistsPerGame: 1.5, fieldGoalPercentage: 48.8, threePointPercentage: 39.8 },
      { id: "gordon", name: "Aaron Gordon", position: "PF", pointsPerGame: 13.5, reboundsPerGame: 6.5, assistsPerGame: 3.2, fieldGoalPercentage: 55.5, threePointPercentage: 28.5 },
      { id: "caldwell", name: "Kentavious Caldwell-Pope", position: "SG", pointsPerGame: 10.2, reboundsPerGame: 2.8, assistsPerGame: 2.2, fieldGoalPercentage: 46.2, threePointPercentage: 40.5 },
    ]
  },
  {
    id: "bucks",
    name: "Bucks",
    city: "Milwaukee",
    abbreviation: "MIL",
    teamPointsPerGame: 119.5,
    teamReboundsPerGame: 46.8,
    teamAssistsPerGame: 26.2,
    teamFieldGoalPercentage: 48.5,
    teamThreePointPercentage: 37.2,
    players: [
      { id: "antetokounmpo", name: "Giannis Antetokounmpo", position: "PF", pointsPerGame: 30.8, reboundsPerGame: 11.2, assistsPerGame: 6.2, fieldGoalPercentage: 60.5, threePointPercentage: 25.8 },
      { id: "lillard", name: "Damian Lillard", position: "PG", pointsPerGame: 24.8, reboundsPerGame: 4.5, assistsPerGame: 7.5, fieldGoalPercentage: 42.5, threePointPercentage: 35.8 },
      { id: "middleton", name: "Khris Middleton", position: "SF", pointsPerGame: 15.2, reboundsPerGame: 5.2, assistsPerGame: 5.2, fieldGoalPercentage: 48.5, threePointPercentage: 38.5 },
      { id: "lopez", name: "Brook Lopez", position: "C", pointsPerGame: 12.8, reboundsPerGame: 5.5, assistsPerGame: 1.2, fieldGoalPercentage: 50.5, threePointPercentage: 36.8 },
      { id: "beasley", name: "Malik Beasley", position: "SG", pointsPerGame: 11.5, reboundsPerGame: 3.8, assistsPerGame: 1.8, fieldGoalPercentage: 44.8, threePointPercentage: 40.2 },
    ]
  },
  {
    id: "heat",
    name: "Heat",
    city: "Miami",
    abbreviation: "MIA",
    teamPointsPerGame: 110.2,
    teamReboundsPerGame: 42.5,
    teamAssistsPerGame: 24.8,
    teamFieldGoalPercentage: 46.8,
    teamThreePointPercentage: 36.2,
    players: [
      { id: "butler", name: "Jimmy Butler", position: "SF", pointsPerGame: 20.8, reboundsPerGame: 5.2, assistsPerGame: 5.5, fieldGoalPercentage: 49.5, threePointPercentage: 33.5 },
      { id: "adebayo", name: "Bam Adebayo", position: "C", pointsPerGame: 19.5, reboundsPerGame: 10.5, assistsPerGame: 4.2, fieldGoalPercentage: 52.5, threePointPercentage: 12.5 },
      { id: "herro", name: "Tyler Herro", position: "SG", pointsPerGame: 20.2, reboundsPerGame: 5.2, assistsPerGame: 4.5, fieldGoalPercentage: 44.5, threePointPercentage: 39.5 },
      { id: "rozier", name: "Terry Rozier", position: "PG", pointsPerGame: 16.8, reboundsPerGame: 3.8, assistsPerGame: 6.2, fieldGoalPercentage: 42.8, threePointPercentage: 36.5 },
      { id: "love", name: "Kevin Love", position: "PF", pointsPerGame: 8.8, reboundsPerGame: 6.2, assistsPerGame: 2.2, fieldGoalPercentage: 44.2, threePointPercentage: 34.8 },
    ]
  }
];

export function getTeamById(id: string): Team | undefined {
  return teams.find(team => team.id === id);
}

export function getPlayerById(teamId: string, playerId: string): Player | undefined {
  const team = getTeamById(teamId);
  return team?.players.find(player => player.id === playerId);
}

