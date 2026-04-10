"use client";

import { useState } from "react";
import Results from "@/components/results";
import Error from "@/components/error";
import MainScreen from "@/components/mainScreen";
import BatchScreen from "@/components/batchScreen";
import { ResultsData } from "@/types/main";

export default function Home() {
  const [results, setResults] = useState<ResultsData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [mode, setMode] = useState<"single" | "batch">("single");

  return (
    <div className="min-h-screen bg-gradient-to-br">
      {results ? (
        <Results results={results} setResults={setResults} setError={setError} />
      ) : error ? (
        <Error error={error} setError={setError} setResults={setResults} />
      ) : (
        <>
          <div className="flex justify-center gap-4 pt-6">
            <button
              onClick={() => setMode("single")}
              className={`px-6 py-2 rounded-full font-semibold transition-all ${
                mode === "single"
                  ? "bg-purple-700 text-white"
                  : "bg-white text-purple-700 border border-purple-700"
              }`}
            >
              Single Repository
            </button>
            <button
              onClick={() => setMode("batch")}
              className={`px-6 py-2 rounded-full font-semibold transition-all ${
                mode === "batch"
                  ? "bg-purple-700 text-white"
                  : "bg-white text-purple-700 border border-purple-700"
              }`}
            >
              Batch Analysis
            </button>
          </div>

          {mode === "single" ? (
            <MainScreen setResults={setResults} />
          ) : (
            <BatchScreen />
          )}
        </>
      )}
    </div>
  );
}