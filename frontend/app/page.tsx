"use client";

import { useState } from "react";
// import axios from "axios";
// import Loading from "@/components/loading";
import Results from "@/components/results";
import Error from "@/components/error";
import MainScreen from "@/components/mainScreen";

/**
 * Main Application Component - UN SDG Advocate
 *
 * Flow:
 * 1. User enters GitHub repository URL
 * 2. Application looks for SDG.md file in the repo and extracts content out of it
 * 3. App calls Flask backend for analysis
 * 4. Results show SDG predictions with confidence levels
 * 5. User can edit predictions via modal interface
 */
export default function Home() {
  // const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);



  return (
    <div className="min-h-screen bg-gradient-to-br">
      {results ? (
        // Results Screen
        <Results
          results={results}
          setResults={setResults}
          setError={setError}
        />
      ) : error ? (
        // Error Screen
        <Error error={error} setError={setError} setResults={setResults} />
      ) : (
        // Main Content (Initial Form)
        <MainScreen setResults={setResults} />
      )}
    </div>
  );
}
