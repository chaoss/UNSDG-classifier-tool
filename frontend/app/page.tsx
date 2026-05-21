"use client";

import { useState } from "react";
import Results from "@/components/results";
import Error from "@/components/error";
import MainScreen from "@/components/mainScreen";
import { ResultsData } from "@/types/main";

/**
 * Main Application Component - UN SDG Advocate
 *
 * Flow:
 * 1. User enters Project Name, GitHub repository URL and project SDG relevance description
 * 2. The data is then sent to Flask backend for analysis
 * 4. Results show SDG predictions with confidence levels
 * 5. User can edit predictions via modal interface
 * 6. Edited results are saved and stored in state
 */
export default function Home() {
  const [results, setResults] = useState<ResultsData | null>(null);
  const [error, setError] = useState<string | null>(null);

  console.log("Current Results State:", results);

  return (
    <div className="min-h-screen bg-gradient-to-br">
      {results ? (
        <Results
          results={results}
          setResults={setResults}
          setError={setError}
        />
      ) : error ? (
        <Error error={error} setError={setError} setResults={setResults} />
      ) : (
        <MainScreen setResults={setResults} setError={setError} />
      )}
    </div>
  );
}
