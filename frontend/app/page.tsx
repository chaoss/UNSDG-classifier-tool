"use client";

import { useState } from "react";
import Goals from "@/assets/UNSDG Goals Image.jpg";
import Image from "next/image";
import { Spinner } from "@/components/spinner";
import axios from "axios";

export default function Home() {
  const [githubUrl, setGithubUrl] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState<{
    sdg_predictions?: Record<string, number>;
    [key: string]: unknown;
  } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editableResults, setEditableResults] = useState<
    Record<string, number>
  >({});
  const [saveMessage, setSaveMessage] = useState<string | null>(null);

  const determineGoals = async () => {
    const response = await axios.post("http://127.0.0.1:5000/api/classify", {
      url: githubUrl,
    });
    return response.data;
  };

  const handlePullRequest = () => {
    // Logic to handle pull request creation
    alert("Pull request started");
    console.log("Pull request creation logic goes here.");
  };

  const handleChanges = () => {
    // Open modal with current SDG predictions for editing
    if (results?.sdg_predictions) {
      setEditableResults({ ...results.sdg_predictions });
      setIsModalOpen(true);
    }
  };

  const saveEditedResults = () => {
    // Update the results with edited values
    if (results) {
      setResults({
        ...results,
        sdg_predictions: editableResults,
      });
    }
    setIsModalOpen(false);
    setSaveMessage("SDG predictions updated successfully!");

    // Clear the message after 3 seconds
    setTimeout(() => {
      setSaveMessage(null);
    }, 3000);
  };

  const updateEditableResult = (sdgKey: string, newValue: number) => {
    setEditableResults((prev) => ({
      ...prev,
      [sdgKey]: newValue,
    }));
  };

  const removeSDG = (sdgKey: string) => {
    setEditableResults((prev) => {
      const updated = { ...prev };
      delete updated[sdgKey];
      return updated;
    });
  };

  const handleInteract = async () => {
    // Check the url if it contains "github.com"
    if (githubUrl.includes("github.com")) {
      setIsLoading(true);
      setError(null);
      setResults(null);
      console.log("Processing GitHub repository:", githubUrl);

      try {
        // Make the actual API call
        const data = await determineGoals();
        setResults(data);
        console.log("Processing completed:", data);
      } catch (error) {
        console.error("Error processing repository:", error);
        setError("Failed to analyze repository. Please try again.");
      } finally {
        setIsLoading(false);
      }
    } else {
      alert("Please enter a valid GitHub repository URL.");
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br">
      {isLoading ? (
        // Loading Screen
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br">
          <div className="text-center space-y-6">
            <Spinner variant="ring" size={64} className="text-purple mx-auto" />
            <div className="space-y-2">
              <h2 className="text-2xl font-bold text-purple">
                Analyzing Repository
              </h2>
              <p className="text-purple-600 text-lg">
                Checking which UN SDG goals your project satisfies...
              </p>
            </div>
          </div>
        </div>
      ) : results ? (
        // Results Screen
        <div className="min-h-screen bg-gradient-to-br">
          <main className="container mx-auto px-8 py-12">
            <div className="space-y-8">
              {/* Header with back button */}
              <div className="flex items-center justify-between">
                <h1 className="text-4xl font-bold text-black">
                  UN SDG Analysis Results
                </h1>
                <button
                  onClick={() => {
                    setResults(null);
                    setError(null);
                    setGithubUrl("");
                    setSaveMessage(null);
                  }}
                  className="px-6 py-3 bg-purple-700 hover:bg-purple-800 text-white font-semibold rounded-xl transition-colors duration-200"
                >
                  Analyze Another Repository
                </button>
              </div>

              {/* Success Message */}
              {saveMessage && (
                <div className="bg-green-50 border border-green-200 text-green-800 px-4 py-3 rounded-lg flex items-center">
                  <svg
                    className="w-5 h-5 mr-2"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M5 13l4 4L19 7"
                    />
                  </svg>
                  {saveMessage}
                </div>
              )}

              {/* Repository URL */}
              <div className="bg-white rounded-xl p-6 shadow-lg">
                <h3 className="text-lg font-semibold text-gray-700 mb-2">
                  Analyzed Repository:
                </h3>
                <p className="text-purple-700 font-medium break-all">
                  {githubUrl}
                </p>
              </div>

              {/* Results Display */}
              <div className="space-y-6">
                <h3 className="text-2xl font-semibold text-gray-800">
                  UN SDG Goals Analysis
                </h3>

                {results?.sdg_predictions ? (
                  <>
                    {/* SDG Cards Grid */}
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                      {Object.entries(results.sdg_predictions)
                        .sort(([, a], [, b]) => Number(b) - Number(a))
                        .map(([sdgKey]) => {
                          // Extract SDG number and name
                          const sdgMatch = sdgKey.match(/SDG (\d+): (.+)/);
                          const sdgNumber = sdgMatch ? sdgMatch[1] : "";
                          const sdgName = sdgMatch ? sdgMatch[2] : sdgKey;

                          return (
                            <div
                              key={sdgKey}
                              className={`border rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow duration-200`}
                            >
                              {/* SDG Header */}
                              <div className="flex items-center justify-between mb-4">
                                <div className="flex items-center space-x-3">
                                  <div className="w-12 h-12 bg-purple-600 rounded-full flex items-center justify-center text-white font-bold text-lg">
                                    {sdgNumber}
                                  </div>
                                  <div>
                                    <h4 className="font-semibold text-gray-800 text-sm">
                                      SDG {sdgNumber}
                                    </h4>
                                  </div>
                                </div>
                              </div>

                              {/* SDG Name */}
                              <h5
                                className="font-medium text-gray-700 mb-3 leading-tight"
                                style={{
                                  display: "-webkit-box",
                                  WebkitLineClamp: 2,
                                  WebkitBoxOrient: "vertical",
                                  overflow: "hidden",
                                }}
                              >
                                {sdgName}
                              </h5>
                            </div>
                          );
                        })}
                    </div>
                    {/* Buttons for "Yes, that's our goal" and "Maybe, we need some edits" */}
                    <div className="flex justify-end mt-6">
                      <button
                        onClick={handlePullRequest}
                        className="cursor-pointer mx-4 px-4 py-2 bg-white text-purple-600 border border-purple-600 rounded-md"
                      >
                        Yes, that&apos;s our goal
                      </button>
                      <button
                        onClick={handleChanges}
                        className="cursor-pointer px-4 py-2 bg-purple-600 text-white rounded-md"
                      >
                        Maybe, we need some edits
                      </button>
                    </div>
                  </>
                ) : (
                  <div className="bg-white rounded-xl p-6 shadow-lg">
                    <h4 className="text-lg font-semibold text-gray-800 mb-2">
                      Raw Results:
                    </h4>
                    <pre className="bg-gray-100 rounded-lg p-4 overflow-auto text-sm">
                      {JSON.stringify(results, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            </div>
          </main>

          {/* Edit SDG Predictions Modal */}
          {isModalOpen && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
              <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
                {/* Modal Header */}
                <div className="bg-purple-600 text-white p-6">
                  <div className="flex items-center justify-between">
                    <h2 className="text-2xl font-bold">Edit SDG Predictions</h2>
                    <button
                      onClick={() => setIsModalOpen(false)}
                      className="text-white hover:text-gray-200 transition-colors"
                    >
                      <svg
                        className="w-6 h-6"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M6 18L18 6M6 6l12 12"
                        />
                      </svg>
                    </button>
                  </div>
                </div>

                {/* Modal Content */}
                <div className="p-6 overflow-y-auto max-h-[60vh]">
                  <div className="space-y-4">
                    {Object.entries(editableResults)
                      .sort(([, a], [, b]) => Number(b) - Number(a))
                      .map(([sdgKey]) => {
                        const sdgMatch = sdgKey.match(/SDG (\d+): (.+)/);
                        const sdgNumber = sdgMatch ? sdgMatch[1] : "";
                        const sdgName = sdgMatch ? sdgMatch[2] : sdgKey;

                        return (
                          <div
                            key={sdgKey}
                            className="border rounded-lg p-4 hover:bg-gray-50 transition-colors"
                          >
                            <div className="flex items-center gap-4">
                              {/* SDG Number */}
                              <div className="w-12 h-12 bg-purple-600 rounded-full flex items-center justify-center text-white font-bold text-sm flex-shrink-0">
                                {sdgNumber}
                              </div>

                              {/* SDG Info */}
                              <div className="flex-1 min-w-0">
                                <h4 className="font-semibold text-gray-800 text-sm">
                                  SDG {sdgNumber}
                                </h4>
                                <p
                                  className="text-gray-600 text-sm truncate"
                                  title={sdgName}
                                >
                                  {sdgName}
                                </p>
                              </div>
                            </div>
                          </div>
                        );
                      })}
                  </div>
                </div>

                {/* Modal Footer */}
                <div className="bg-gray-50 px-6 py-4 flex justify-end gap-3">
                  <button
                    onClick={() => setIsModalOpen(false)}
                    className="px-4 py-2 text-gray-600 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={saveEditedResults}
                    className="px-6 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 transition-colors"
                  >
                    Save Changes
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      ) : error ? (
        // Error Screen
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br">
          <div className="text-center space-y-6 max-w-md">
            <div className="text-red-500">
              <svg
                className="w-16 h-16 mx-auto mb-4"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
            <div className="space-y-2">
              <h2 className="text-2xl font-bold text-red-600">
                Analysis Failed
              </h2>
              <p className="text-gray-600 text-lg">{error}</p>
            </div>
            <button
              onClick={() => {
                setError(null);
                setResults(null);
              }}
              className="px-6 py-3 bg-purple-700 hover:bg-purple-800 text-white font-semibold rounded-xl transition-colors duration-200"
            >
              Try Again
            </button>
          </div>
        </div>
      ) : (
        // Main Content (Initial Form)
        <main className="container mx-auto px-8 py-12">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            {/* Left Content */}
            <div className="space-y-8">
              <div className="space-y-6">
                <h1 className="text-6xl font-bold text-black leading-tight">
                  Check which{" "}
                  <span className="text-purple-700">UN SDG goals</span> your
                  project satisfy
                </h1>
                <p className="text-xl text-gray-800 leading-relaxed">
                  A simple tool that identifies relevant UN Sustainable
                  Development Goals (SDGs) based on the content of a Github
                  repository.
                </p>
              </div>

              {/* Input Section */}
              <div className="space-y-4">
                <div className="flex gap-4">
                  <input
                    type="text"
                    placeholder="Paste your github repository link here.."
                    value={githubUrl}
                    onChange={(e) => setGithubUrl(e.target.value)}
                    className="flex-1 px-6 py-4 rounded-2xl border-0 text-gray-600 placeholder-gray-400 text-lg shadow-sm focus:outline-none"
                  />
                  <button
                    onClick={handleInteract}
                    disabled={isLoading}
                    className="px-8 py-4 bg-purple-700 hover:bg-purple-800 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold rounded-2xl transition-colors duration-200 shadow-lg"
                  >
                    Generate
                  </button>
                </div>
              </div>
            </div>

            {/* Right Illustration */}
            <div className="flex justify-center lg:justify-end">
              <Image
                src={Goals}
                alt="UN SDG Goals"
                className="max-w-full h-auto"
              />
            </div>
          </div>
        </main>
      )}
    </div>
  );
}
