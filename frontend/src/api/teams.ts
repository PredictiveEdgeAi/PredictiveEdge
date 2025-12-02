export interface Team {
  id: string;
  name: string;
  city: string;
  abbreviation: string;
  fullName: string;
}

export async function getTeams(): Promise<Team[]> {
  const response = await fetch("http://localhost:8000/teams", {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  });
  
  if (!response.ok) {
    throw new Error("Failed to fetch teams");
  }
  
  const data = await response.json();
  return data.teams;
}

