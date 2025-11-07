export async function getPrediction(inputData: { 
  teamPointsPerGame: number; 
  opponentPointsPerGame: number;
  fieldGoalPercentage: number;
  threePointPercentage: number;
  reboundsPerGame: number;
  assistsPerGame: number;
}) {
  const response = await fetch("http://127.0.0.1:8000/predict", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(inputData),
  });
  
  if (!response.ok) {
    throw new Error("Failed to get analysis");
  }
  
  const data = await response.json();
  return data.prediction;
}
