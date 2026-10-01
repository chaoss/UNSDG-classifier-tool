import { useState } from "react";
import JSZip from "jszip";
import { MdDone } from "react-icons/md";
import CardGrid from "./cardGrid";
import RawResults from "./rawResults";
import EditModal from "./editModal";
import { SDGValue, ResultsData } from "@/types/main";
import NoSdgPage from "./noSdgPage"

/*
Results Component
- Displays the results of the SDG analysis
- Shows SDG cards, allows editing via modal, and downloading results
*/

type ResultsProps = {
  results: ResultsData | null;
  setResults: (value: ResultsData | null) => void;
  setError: (value: string | null) => void;
};

const isNoSdgs = (predictions: ResultsData["predictions"]): boolean => {
  if (predictions == null) return true;

  if (Array.isArray(predictions)) {
    return predictions.length === 0;
  }

  if (typeof predictions !== "object") return true;

  const keys = Object.keys(predictions);
  if (keys.length === 0) return true;

  const values = Object.values(predictions as Record<string, unknown>);
  return values.every((v) => {
    if (v == null) return true;
    if (typeof v === "number") return v <= 0;
    if (typeof v === "object" && v !== null && "prediction" in v) {
      const sdgValue = v as SDGValue;
      const num = Number(sdgValue.prediction);
      return !Number.isFinite(num) || num <= 0;
    }
    return true;
  });
};

const Results = ({ results, setResults, setError }: ResultsProps) => {
  const [editableResults, setEditableResults] = useState<
    Record<string, SDGValue>
  >({});

  const [saveMessage, setSaveMessage] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [confidenceThreshold, setConfidenceThreshold] = useState(0);

  const getScore = (v: number | SDGValue | null | undefined) =>
    typeof v === "number"
      ? Number(v)
      : v && typeof v.prediction === "number"
        ? Number(v.prediction)
        : 0;

  const saveEditedResults = () => {
    if (results) {
      setResults({
        ...results,
        predictions: { ...(editableResults ?? {}) },
      });
    }
    setIsModalOpen(false);
    setSaveMessage("SDG predictions updated successfully!");

    setTimeout(() => {
      setSaveMessage(null);
    }, 3000);
  };

  const handleChanges = () => {
    if (results?.predictions) {
      const normalized: Record<string, SDGValue> = {};
      Object.entries(
        results.predictions as Record<string, number | SDGValue>,
      ).forEach(([k, v]) => {
        if (typeof v === "number") {
          normalized[k] = { prediction: v };
        } else {
          normalized[k] = v as SDGValue;
        }
      });
      setEditableResults(normalized);
      setIsModalOpen(true);
    }
  };

  const buildDownloadContent = (
    predictions: Record<string, number | SDGValue>,
    format: "json" | "yaml" | "txt",
  ) => {
    const unsdgData = {
      sdg_analysis: {
        analyzed_at: new Date().toISOString(),
        repositoryName: results?.projectName,
        repositoryUrl: results?.projectUrl,
        predictions,
        summary: {
          total_sdgs: Object.keys(predictions).length,
          high_confidence: Object.values(predictions).filter(
            (score) => getScore(score) >= 0.7,
          ).length,
          medium_confidence: Object.values(predictions).filter(
            (score) => getScore(score) >= 0.4 && getScore(score) < 0.7,
          ).length,
          low_confidence: Object.values(predictions).filter(
            (score) => getScore(score) < 0.4,
          ).length,
        },
      },
    };

    if (format === "json") {
      return {
        content: JSON.stringify(unsdgData, null, 2),
        fileName: "unsdg.json",
        mimeType: "application/json",
      };
    }

    if (format === "yaml") {
      const lines = [
        "sdg_analysis:",
        `  analyzed_at: "${new Date().toISOString()}"`,
        `  repositoryName: "${String(results?.projectName ?? "").replace(/"/g, '\\"')}"`,
        `  repositoryUrl: "${String(results?.projectUrl ?? "").replace(/"/g, '\\"')}"`,
        "  predictions:",
      ];

      Object.entries(predictions).forEach(([key, value]) => {
        if (typeof value === "number") {
          lines.push(`    ${key}: ${value}`);
        } else {
          lines.push(`    ${key}: ${JSON.stringify(value)}`);
        }
      });

      lines.push("  summary:");
      lines.push(`    total_sdgs: ${Object.keys(predictions).length}`);
      lines.push(
        `    high_confidence: ${Object.values(predictions).filter((score) => getScore(score) >= 0.7).length}`,
      );
      lines.push(
        `    medium_confidence: ${Object.values(predictions).filter((score) => getScore(score) >= 0.4 && getScore(score) < 0.7).length}`,
      );
      lines.push(
        `    low_confidence: ${Object.values(predictions).filter((score) => getScore(score) < 0.4).length}`,
      );

      return {
        content: lines.join("\n"),
        fileName: "unsdg.yaml",
        mimeType: "text/yaml",
      };
    }

    const textLines = [
      `Repository: ${results?.projectName ?? "N/A"}`,
      `URL: ${results?.projectUrl ?? "N/A"}`,
      `Analysis generated: ${new Date().toISOString()}`,
      "",
      "SDG Predictions:",
    ];

    Object.entries(predictions).forEach(([key, value]) => {
      textLines.push(`${key}: ${getScore(value).toFixed(4)}`);
    });

    return {
      content: textLines.join("\n"),
      fileName: "unsdg.txt",
      mimeType: "text/plain",
    };
  };

  const handleDownload = async () => {
    if (!results?.predictions || isNoSdgs(results.predictions)) {
      setError("No SDG predictions available.");
      return;
    }

    try {
      const predictions = results.predictions as Record<string, number | SDGValue>;
      const zip = new JSZip();

      const files = [
        buildDownloadContent(predictions, "json"),
        buildDownloadContent(predictions, "yaml"),
        buildDownloadContent(predictions, "txt"),
      ];

      files.forEach((file) => {
        zip.file(file.fileName, file.content);
      });

      const archiveBlob = await zip.generateAsync({ type: "blob" });
      const url = URL.createObjectURL(archiveBlob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "unsdg-analysis.zip";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      setSaveMessage("SDG analysis folder downloaded successfully!");

      setTimeout(() => {
        setSaveMessage(null);
      }, 3000);
    } catch {
      setError("Failed to create the download archive.");
    }
  };

  const noSdgs = isNoSdgs(results?.predictions);
  const recommendation = results?.recommendation;
  const visiblePredictions = Object.fromEntries(
    Object.entries(results?.predictions ?? {}).filter(([, value]) =>
      getScore(value as number | SDGValue) >= confidenceThreshold,
    ),
  );

  return (
    <div className="min-h-screen bg-gradient-to-br">
      <main className="container mx-auto px-8 py-12">
        <div className="space-y-8">
          {/* Header with back button */}
          <div className="flex items-center justify-between">
            <h1 className="text-4xl font-bold text-black">UN SDG Analysis Results</h1>
            <button
              onClick={() => {
                setResults(null);
                setError(null);
                setSaveMessage(null);
              }}
              className="px-6 py-3 bg-[#5b92e5] hover:bg-[#4d82d6] text-white font-semibold rounded-xl transition-colors duration-200"
            >
              Analyze Another Repository
            </button>
          </div>

          {/* Success Message */}
          {saveMessage && (
            <div className="bg-green-50 border border-green-200 text-green-800 px-4 py-3 rounded-lg flex items-center">
              <MdDone className="mr-2" />
              {saveMessage}
            </div>
          )}

          {/* Repository URL */}
          <div className="bg-white rounded-xl p-6 shadow-lg">
            <h3 className="text-lg font-semibold text-gray-700 mb-2">Analyzed Repository:</h3>
            <p className="text-[#5b92e5] font-medium break-all">{results?.projectUrl ?? "—"}</p>
          </div>

          {/* Results Display */}
          <div className="space-y-6">
            <h3 className="text-2xl font-semibold text-gray-800">UN SDG Goals Analysis</h3>
            {results ? (
              noSdgs ? (
                <NoSdgPage recommendation={recommendation} />
              ) : (
                <>
                  <div className="flex items-start gap-6">
                    <div className="min-w-0 flex-1">
                      {Object.keys(visiblePredictions).length > 0 ? (
                        <CardGrid sdgPredictions={visiblePredictions} />
                      ) : (
                        <p className="py-12 text-center text-gray-600">
                          No results meet this confidence threshold.
                        </p>
                      )}
                    </div>
                    <aside className="sticky top-6 flex shrink-0 flex-col items-center gap-3 rounded-lg border border-gray-200 bg-white px-4 py-5 shadow-sm">
                      <label
                        htmlFor="confidence-threshold"
                        className="max-w-24 text-center text-sm font-semibold text-gray-800"
                      >
                        Minimum relevance
                      </label>
                      <output
                        htmlFor="confidence-threshold"
                        className="text-lg font-bold text-gray-900"
                      >
                        {Math.round(confidenceThreshold * 100)}%
                      </output>
                      <span className="text-xs font-medium text-green-700">High</span>
                      <input
                        id="confidence-threshold"
                        type="range"
                        min="0"
                        max="1"
                        step="0.01"
                        value={confidenceThreshold}
                        onChange={(event) =>
                          setConfidenceThreshold(Number(event.target.value))
                        }
                        aria-label="Minimum prediction relevance"
                        className="confidence-slider h-52 w-6 cursor-pointer"
                      />
                      <span className="text-xs font-medium text-red-700">Low</span>
                      <span className="text-xs text-gray-500">
                        {Object.keys(visiblePredictions).length} shown
                      </span>
                    </aside>
                  </div>

                  <div className="flex flex-wrap items-center justify-end gap-3 mt-6">
                    <button
                      onClick={handleDownload}
                      className="cursor-pointer px-4 py-2 bg-white text-[#5b92e5] border border-[#5b92e5] rounded-md hover:bg-[#edf4ff] disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
                    >
                      <span className="flex items-center">Download SDG Analysis Bundle</span>
                    </button>
                    <button
                      onClick={handleChanges}
                      className="cursor-pointer px-4 py-2 bg-[#5b92e5] text-white rounded-md hover:bg-[#4d82d6] transition-colors duration-200"
                    >
                      Maybe, we need some edits
                    </button>
                  </div>
                </>
              )
            ) : (
              <RawResults results={results} />
            )}
          </div>
        </div>
      </main>

      {/* Edit SDG Predictions Modal */}
      {isModalOpen && results && !noSdgs && (
        <EditModal
          editableResults={editableResults || {}}
          setEditableResults={setEditableResults}
          setIsModalOpen={setIsModalOpen}
          saveEditedResults={saveEditedResults}
        />
      )}
    </div>
  );
};

export default Results;

