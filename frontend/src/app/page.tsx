"use client";

import { useState } from "react";
import { getPrediction } from "../api/predict";

export default function HomePage() {
  const [input, setInput] = useState({ feature1: "", feature2: "" });
  const [result, setResult] = useState<string | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInput({ ...input, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const prediction = await getPrediction({
      feature1: parseFloat(input.feature1),
      feature2: parseFloat(input.feature2),
    });
    setResult(prediction);
  };

  return (
    <main style={{ padding: "2rem", fontFamily: "Arial" }}>
      <h1>🏀 PredictiveEdge</h1>
      <p>AI-powered sports analytics platform</p>
      <form onSubmit={handleSubmit} style={{ marginTop: "1rem" }}>
        <input
          name="feature1"
          type="number"
          placeholder="Feature 1"
          onChange={handleChange}
          style={{ marginRight: "0.5rem" }}
        />
        <input
          name="feature2"
          type="number"
          placeholder="Feature 2"
          onChange={handleChange}
        />
        <button type="submit" style={{ marginLeft: "0.5rem" }}>Analyze</button>
      </form>
      {result && <h2 style={{ marginTop: "1rem" }}>Model Estimate: {result}</h2>}
    </main>
  );
}

