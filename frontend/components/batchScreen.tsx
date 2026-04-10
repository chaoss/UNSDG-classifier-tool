"use client";
import { useState } from "react";
import { AiOutlineLoading3Quarters } from "react-icons/ai";
import { classifyBatch } from "@/services/api";
import { BatchResult } from "@/types/main";

const BatchScreen = () => {
  const [urlsText, setUrlsText] = useState("");
  const [description, setDescription] = useState("");
  const [results, setResults] = useState<BatchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleAnalyze = async () => {
    const lines = urlsText
      .split("\n")
      .map((l) => l.trim())
      .filter((l) => l.includes("github.com"));

    if (lines.length === 0) {
      setError("Please enter at least one valid GitHub URL.");
      return;
    }
    if (lines.length > 20) {
      setError("Maximum 20 repositories allowed.");
      return;
    }
    if (!description.trim()) {
      setError("Please enter a common description.");
      return;
    }

    setError("");
    setLoading(true);
    setResults([]);

    const repositories = lines.map((url) => ({
      projectName: url.split("/").pop() || url,
      projectUrl: url,
      projectDescription: description,
    }));

    try {
      const data = await classifyBatch(repositories);
      setResults(data.results);
    } catch {
      setError("Batch analysis failed. Make sure backend is running.");
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadCSV = () => {
    const header = "Project Name,URL,Top SDG,Confidence,Status\n";
    const rows = results
      .map(
        (r) =>
          `"${r.projectName}","${r.projectUrl}","${r.topSdg || "N/A"}",${
            r.confidence ? (r.confidence * 100).toFixed(1) + "%" : "N/A"
          },${r.status}`
      )
      .join("\n");
    const blob = new Blob([header + rows], { type: "text/csv" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "batch_sdg_analysis.csv";
    a.click();
  };

  const handleDownloadJSON = () => {
    const blob = new Blob([JSON.stringify({ results }, null, 2)], {
      type: "application/json",
    });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "batch_sdg_analysis.json";
    a.click();
  };

  return (
    <div className="text-center px-8 py-16 bg-purple-400">
      <div className="max-w-3xl mx-auto">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-white mb-2">
            Batch Repository Analysis
          </h2>
          <p className="text-white text-sm">
            Analyze up to 20 GitHub repositories at once
          </p>
        </div>

        <div className="space-y-6">
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2 text-left">
              GitHub URLs (one per line)
              <span className="text-red-500 ml-1">*</span>
            </label>
            <textarea
              value={urlsText}
              onChange={(e) => setUrlsText(e.target.value)}
              placeholder={"https://github.com/oppia/oppia\nhttps://github.com/facebook/react"}
              rows={6}
              disabled={loading}
              className="w-full bg-white px-6 py-4 rounded-2xl border border-gray-200 text-gray-700 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all font-mono text-sm"
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2 text-left">
              Common SDG Relevance Description
              <span className="text-red-500 ml-1">*</span>
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Describe the SDG relevance common to these projects (100-120 words recommended)"
              rows={5}
              disabled={loading}
              className="w-full bg-white px-6 py-4 rounded-2xl border border-gray-200 text-gray-700 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
            />
          </div>

          {error && (
            <div className="p-4 rounded-2xl bg-red-50 text-red-700 border border-red-200 text-left">
              {error}
            </div>
          )}

          {loading && (
            <p className="text-white text-sm">
              Processing repositories sequentially to respect API rate limits...
            </p>
          )}

          <button
            onClick={handleAnalyze}
            disabled={loading}
            className="w-full px-8 py-4 bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold rounded-2xl transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <AiOutlineLoading3Quarters className="animate-spin h-5 w-5" />
                Analyzing...
              </span>
            ) : (
              "Analyze All Repositories"
            )}
          </button>
        </div>

        {results.length > 0 && (
          <div className="mt-10">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-white font-semibold text-lg">
                Results ({results.length} repositories)
              </h3>
              <div className="flex gap-2">
                <button
                  onClick={handleDownloadCSV}
                  className="text-sm bg-white text-purple-700 px-3 py-1 rounded-lg hover:bg-purple-50"
                >
                  Download CSV
                </button>
                <button
                  onClick={handleDownloadJSON}
                  className="text-sm bg-white text-purple-700 px-3 py-1 rounded-lg hover:bg-purple-50"
                >
                  Download JSON
                </button>
              </div>
            </div>

            <div className="overflow-x-auto rounded-2xl border bg-white">
              <table className="w-full text-sm text-left">
                <thead className="bg-purple-50">
                  <tr>
                    <th className="p-4 font-semibold text-gray-700">Repository</th>
                    <th className="p-4 font-semibold text-gray-700">Top SDG</th>
                    <th className="p-4 font-semibold text-gray-700">Confidence</th>
                    <th className="p-4 font-semibold text-gray-700">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {results.map((r, i) => (
                    <tr key={i} className="border-t hover:bg-gray-50">
                      <td className="p-4">
                        <a
                          href={r.projectUrl}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-purple-600 hover:underline"
                        >
                          {r.projectName}
                        </a>
                      </td>
                      <td className="p-4 text-gray-700">{r.topSdg || "—"}</td>
                      <td className="p-4 text-gray-700">
                        {r.confidence
                          ? `${(r.confidence * 100).toFixed(1)}%`
                          : "—"}
                      </td>
                      <td className="p-4">
                        {r.status === "success" ? (
                          <span className="text-green-600 font-medium">Success</span>
                        ) : (
                          <span className="text-red-500">Failed: {r.error}</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default BatchScreen;