import { useState } from "react";
import { MdDone } from "react-icons/md";
import CardGrid from "./cardGrid";
import SummaryCard from "./summaryCard";
import RawResults from "./rawResults";
import EditModal from "./editModal";

// add local SDGValue type to match editModal
type SDGValue = {
  prediction: number;
  sdg?: {
    "@type"?: string;
    code?: string;
    icon?: string;
    id?: string;
    label?: string;
    name?: string;
    type?: string;
    [k: string]: any;
  };
};

type ResultsData = {
  projectUrl?: string;
  projectName?: string;
  // predictions now can be the object shape produced by the classifier / editor
  predictions?: Record<string, SDGValue> | Record<string, number>;
  [key: string]: unknown;
};

type ResultsProps = {
  results: ResultsData | null;
  setResults: (value: ResultsData | null) => void;
  setError: (value: string | null) => void;
};

const Results = ({ results, setResults, setError }: ResultsProps) => {
  // editableResults holds the full SDGValue objects (not just numbers)
  const [editableResults, setEditableResults] = useState<
    Record<string, SDGValue> | undefined
  >({});

  const [saveMessage, setSaveMessage] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const getScore = (v: any) =>
    typeof v === "number" ? Number(v) : Number(v?.prediction ?? 0);

  const saveEditedResults = () => {
    // Update the results with edited values
    if (results) {
      setResults({
        ...results,
        // store the full editableResults object into results.predictions
        predictions: { ...(editableResults ?? {}) },
      });
    }
    setIsModalOpen(false);
    setSaveMessage("SDG predictions updated successfully!");

    // Clear the message after 3 seconds
    setTimeout(() => {
      setSaveMessage(null);
    }, 3000);
  };

  const handleChanges = () => {
    // Open modal with current SDG predictions for editing
    if (results?.predictions) {
      // normalize predictions into the SDGValue shape if they are plain numbers
      const normalized: Record<string, SDGValue> = {};
      Object.entries(results.predictions as Record<string, any>).forEach(
        ([k, v]) => {
          if (typeof v === "number") {
            normalized[k] = { prediction: v };
          } else {
            normalized[k] = v as SDGValue;
          }
        }
      );
      setEditableResults(normalized);
      setIsModalOpen(true);
    }
  };

  const handleDownload = () => {
    if (!results?.predictions) {
      setError("No SDG predictions available to create pull request.");
      return;
    }
    try {
      const predictions = results.predictions as Record<string, any>;
      const unsdgData = {
        sdg_analysis: {
          analyzed_at: new Date().toISOString(),
          repositoryName: results.projectName,
          repositoryUrl: results.projectUrl,
          predictions,
          summary: {
            total_sdgs: Object.keys(predictions).length,
            high_confidence: Object.values(predictions).filter(
              (score) => getScore(score) >= 0.7
            ).length,
            medium_confidence: Object.values(predictions).filter(
              (score) => getScore(score) >= 0.4 && getScore(score) < 0.7
            ).length,
            low_confidence: Object.values(predictions).filter(
              (score) => getScore(score) < 0.4
            ).length,
          },
        },
      };

      // Convert to JSON string and create a Blob for download
      const jsonString = JSON.stringify(unsdgData, null, 2);
      const blob = new Blob([jsonString], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "unsdg.json";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      setSaveMessage("SDG analysis file downloaded successfully!");

      setTimeout(() => {
        setSaveMessage(null);
      }, 3000);
    } catch {
      setError("Failed to create json file for download.");
    }
  };

  return (
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
              <MdDone className="mr-2" />
              {saveMessage}
            </div>
          )}

          {/* Repository URL */}
          <div className="bg-white rounded-xl p-6 shadow-lg">
            <h3 className="text-lg font-semibold text-gray-700 mb-2">
              Analyzed Repository:
            </h3>
            <p className="text-purple-700 font-medium break-all">
              {results?.projectUrl ?? "—"}
            </p>
          </div>
          {/* Results Display */}
          <div className="space-y-6">
            <h3 className="text-2xl font-semibold text-gray-800">
              UN SDG Goals Analysis
            </h3>

            {results ? (
              <>
                {/* Summary Card */}
                {/* <SummaryCard predictions={results?.predictions} /> */}
                {/* SDG Cards Grid */}
                <CardGrid sdgPredictions={results.predictions} />
                {/* Action Buttons */}
                <div className="flex justify-end mt-6">
                  <button
                    onClick={handleDownload}
                    className="cursor-pointer mx-4 px-4 py-2 bg-white text-purple-600 border border-purple-600 rounded-md hover:bg-purple-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
                  >
                    <span className="flex items-center">
                      Yes, Download SDG Analysis File
                    </span>
                  </button>
                  <button
                    onClick={handleChanges}
                    className="cursor-pointer px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 transition-colors duration-200"
                  >
                    Maybe, we need some edits
                  </button>
                </div>
              </>
            ) : (
              <RawResults results={results} />
            )}
          </div>
        </div>
      </main>

      {/* Edit SDG Predictions Modal */}
      {isModalOpen && (
        <EditModal
          // EditModal expects Record<string, SDGValue>, ensure we pass an object
          editableResults={editableResults ?? {}}
          setEditableResults={setEditableResults}
          setIsModalOpen={setIsModalOpen}
          saveEditedResults={saveEditedResults}
        />
      )}
    </div>
  );
};

export default Results;
