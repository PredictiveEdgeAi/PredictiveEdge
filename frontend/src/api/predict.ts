export interface PredictionResponse {
  prediction: string;
  home_win_probability: number;
  away_win_probability: number;
}

export async function getPrediction(inputData: { 
  home_team_name: string;
  away_team_name: string;
}): Promise<PredictionResponse> {
  const response = await fetch("http://localhost:8000/predict", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(inputData),
  });
  
  if (!response.ok) {
    throw new Error("Failed to get analysis");
  }
  
  const data = await response.json();
  return data;
}
