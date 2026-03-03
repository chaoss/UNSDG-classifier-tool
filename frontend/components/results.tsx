import { useState } from "react";
import { MdDone } from "react-icons/md";
import { AiOutlineLoading3Quarters } from "react-icons/ai";
import CardGrid from "./cardGrid";
import RawResults from "./rawResults";
import EditModal from "./editModal";
import { SDGValue, ResultsData } from "@/types/main";
import { IoIosInformationCircleOutline } from "react-icons/io";
import { classifyByModel } from "@/services/api";
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

const Results = ({ results, setResults, setError }: ResultsProps) => {
  const [editableResults, setEditableResults] = useState<
    Record<string, SDGValue>
  >({});

  const [saveMessage, setSaveMessage] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<string>("aurora");
  const [isLoadingTab, setIsLoadingTab] = useState(false);

  const handleTabChange = async (newTab: string) => {
    if (newTab === activeTab || !results) return;

    setIsLoadingTab(true);
    setActiveTab(newTab);

    const requestData = {
      projectName:
        localStorage.getItem("projectName") || results.projectName || "",
      projectUrl:
        localStorage.getItem("projectUrl") || results.projectUrl || "",
      projectDescription:
        localStorage.getItem("projectDescription") ||
        results.projectDescription ||
        "",
    };

    try {
      // const base = "http://127.0.0.1:5000/";
      // let endpoint = "";

      // switch (newTab) {
      //   case "aurora":
      //     endpoint = "api/classify_aurora";
      //     break;
      //   case "st-description":
      //     endpoint = "api/classify_st_description";
      //     break;
      //   case "st-url":
      //     endpoint = "api/classify_st_url";
      //     break;
      //   default:
      //     endpoint = "api/classify_aurora";
      // }

      // const response = await axios.post(base + endpoint, requestData, {
      //   headers: {
      //     "Content-Type": "application/json",
      //   },
      // });

      const response = await classifyByModel(
        newTab as "aurora" | "st-description" | "st-url",
        requestData,
      );

      if (response) {
        setResults(response as ResultsData);
      }
    } catch (error) {
      console.error("Error fetching data for tab:", error);
      setError("Failed to load data for selected model. Please try again.");
    } finally {
      setIsLoadingTab(false);
    }
  };

  const getScore = (v: number | SDGValue | null | undefined) =>
    typeof v === "number"
      ? Number(v)
      : Number((v as SDGValue)?.prediction ?? 0);

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

  const handleDownload = () => {
    if (!results?.predictions) {
      setError("No SDG predictions available.");
      return;
    }
    try {
      const predictions = results.predictions as Record<
        string,
        number | SDGValue
      >;
      const unsdgData = {
        sdg_analysis: {
          analyzed_at: new Date().toISOString(),
          repositoryName: results.projectName,
          repositoryUrl: results.projectUrl,
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

            {/* Vertical Tabs Layout */}
            <div className="flex gap-6">
              {/* Sidebar Navigation */}
              <div className="w-64 flex-shrink-0">
                <div className="bg-white rounded-xl shadow-lg p-2 space-y-1">
                  <h4 className="text-sm font-semibold text-gray-600 px-4 py-2">
                    Available Models
                  </h4>

                  <button
                    onClick={() => handleTabChange("aurora")}
                    disabled={isLoadingTab}
                    className={`w-full text-left px-4 py-3 rounded-lg transition-all duration-200 relative ${
                      activeTab === "aurora"
                        ? "bg-purple-50 text-purple-700 font-semibold"
                        : "text-gray-700 hover:bg-gray-50"
                    } disabled:opacity-50 disabled:cursor-not-allowed`}
                  >
                    {activeTab === "aurora" && (
                      <div className="absolute left-0 top-1/2 transform -translate-y-1/2 w-1 h-8 bg-purple-600 rounded-r-full"></div>
                    )}
                    <span className="ml-2 flex items-center">
                      Aurora Model
                      <span className="relative group inline-block">
                        <IoIosInformationCircleOutline className="ml-2 text-purple-600 cursor-help" />
                        <span className="invisible group-hover:visible absolute left-1/2 -translate-x-1/2 bottom-full mb-2 w-48 px-3 py-2 text-xs text-white bg-gray-800 rounded-lg shadow-lg z-10 whitespace-normal">
                          This is a third party API from EU Alliance Research
                          <span className="absolute top-full left-1/2 -translate-x-1/2 -mt-1 border-4 border-transparent border-t-gray-800"></span>
                        </span>
                      </span>
                    </span>
                  </button>

                  <button
                    onClick={() => handleTabChange("st-description")}
                    disabled={isLoadingTab}
                    className={`w-full text-left px-4 py-3 rounded-lg transition-all duration-200 relative ${
                      activeTab === "st-description"
                        ? "bg-purple-50 text-purple-700 font-semibold"
                        : "text-gray-700 hover:bg-gray-50"
                    } disabled:opacity-50 disabled:cursor-not-allowed`}
                  >
                    {activeTab === "st-description" && (
                      <div className="absolute left-0 top-1/2 transform -translate-y-1/2 w-1 h-8 bg-purple-600 rounded-r-full"></div>
                    )}
                    <span className="ml-2">
                      Sentence Transformer Description
                      <span className="relative group inline-block">
                        <IoIosInformationCircleOutline className="ml-2 text-purple-600 cursor-help" />
                        <span className="invisible group-hover:visible absolute left-1/2 -translate-x-1/2 bottom-full mb-2 w-48 px-3 py-2 text-xs text-white bg-gray-800 rounded-lg shadow-lg z-10 whitespace-normal">
                          This is a sentence transformer modal from Huggingface
                          that analyzes the project description.
                          <span className="absolute top-full left-1/2 -translate-x-1/2 -mt-1 border-4 border-transparent border-t-gray-800"></span>
                        </span>
                      </span>
                    </span>
                  </button>

                  <button
                    onClick={() => handleTabChange("st-url")}
                    disabled={isLoadingTab}
                    className={`w-full text-left px-4 py-3 rounded-lg transition-all duration-200 relative ${
                      activeTab === "st-url"
                        ? "bg-purple-50 text-purple-700 font-semibold"
                        : "text-gray-700 hover:bg-gray-50"
                    } disabled:opacity-50 disabled:cursor-not-allowed`}
                  >
                    {activeTab === "st-url" && (
                      <div className="absolute left-0 top-1/2 transform -translate-y-1/2 w-1 h-8 bg-purple-600 rounded-r-full"></div>
                    )}
                    <span className="ml-2">
                      Sentence Transformer URL
                      <span className="relative group inline-block">
                        <IoIosInformationCircleOutline className="ml-2 text-purple-600 cursor-help" />
                        <span className="invisible group-hover:visible absolute left-1/2 -translate-x-1/2 bottom-full mb-2 w-48 px-3 py-2 text-xs text-white bg-gray-800 rounded-lg shadow-lg z-10 whitespace-normal">
                          This is a sentence transformer modal from Huggingface
                          that analyzes the github repository URL and all its
                          metadata.
                          <span className="absolute top-full left-1/2 -translate-x-1/2 -mt-1 border-4 border-transparent border-t-gray-800"></span>
                        </span>
                      </span>
                    </span>
                  </button>
                </div>
              </div>

              {/* Main Content Area */}
              <div className="flex-1">
                {isLoadingTab ? (
                  <div className="flex items-center justify-center py-20">
                    <AiOutlineLoading3Quarters className="animate-spin text-purple-600 text-4xl" />
                    <span className="ml-3 text-gray-600">
                      Loading model results...
                    </span>
                  </div>
                ) : results ? (
                  <>
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
          </div>
        </div>
      </main>

      {/* Edit SDG Predictions Modal */}
      {isModalOpen && (
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
