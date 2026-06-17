import React, { useState } from "react";
import Goals from "@/assets/UNSDG Goals Image.jpg";
import Image from "next/image";
import { TiTick } from "react-icons/ti";
import { ImCross } from "react-icons/im";
import { AiOutlineLoading3Quarters } from "react-icons/ai";
import { ResultsData } from "@/types/main";
import { sdgApi } from "@/services/api";

/*
MainScreen Component
- Renders the main screen with project input form
- Handles form submission and API interaction

*/

const MainScreen: React.FC<{
  setResults: React.Dispatch<React.SetStateAction<ResultsData | null>>;
}> = ({ setResults }) => {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadMsg, setUploadMsg] = useState<string | null>(null);

  const [projectName, setProjectName] = useState("");
  const [projectUrl, setProjectUrl] = useState("");
  const [projectDescription, setProjectDescription] = useState("");
  // const [problemStatement, setProblemStatement] = useState("");
  // const [longTermGoal, setLongTermGoal] = useState("");
  // const [solutionApproach, setSolutionApproach] = useState("");
  // const [targetAudience, setTargetAudience] = useState("");

  const handleFormSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (
      !projectName ||
      !projectUrl ||
      !projectDescription
      // !problemStatement ||
      // !longTermGoal ||
      // !solutionApproach ||
      // !targetAudience
    ) {
      setUploadMsg("Please fill in all required fields before submitting.");
      return;
    }

    if (projectUrl.includes("github.com") === false) {
      setUploadMsg("Please enter a valid GitHub repository URL.");
      return;
    }

    const finalizedData = {
      projectName: projectName,
      projectUrl: projectUrl,
      projectDescription: projectDescription,
    };

    localStorage.setItem("projectDescription", projectDescription);
    localStorage.setItem("projectName", projectName);
    localStorage.setItem("projectUrl", projectUrl);

    try {
      setIsUploading(true);
      setUploadMsg(null);

      const response = await sdgApi.classifyAurora(finalizedData);

      if (response && response.repo_url) {
        setUploadMsg("Text Analyzing Successfully!");
      }

      // const base = "http://127.0.0.1:5000/";
      // const response = await axios.post(
      //   base + "api/classify_aurora",
      //   finalizedData,
      //   {
      //     headers: {
      //       "Content-Type": "application/json",
      //     },
      //   },
      // );

      // if (!response.statusText || response.statusText !== "OK") {
      //   throw new Error(response.data.error);
      // }
      // if (response.data && response.data.repo_url) {
      //   setUploadMsg("Text Analyzing Successfully!");
      // }

      // console.log("API Response:", response.data);
      setResults(response as ResultsData);
    } catch (error) {
      console.error("Error:", error);
      setUploadMsg("Text Analyzing Failed. Please try again.");
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div>
      <div className="container mx-auto px-12 py-12">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          {/* Main Content */}
          <div className="space-y-8">
            <div className="space-y-6">
              <h1 className="text-6xl font-bold text-foreground leading-tight">
                Check which{" "}
                <span className="text-purple-700 dark:text-purple-400">UN SDG goals</span> your
                project satisfy
              </h1>
              <p className="text-xl text-muted-foreground leading-relaxed">
                A simple tool that identifies relevant UN Sustainable
                Development Goals (SDGs) based on the content of a Github
                repository.
              </p>
            </div>
          </div>

          <div className="flex justify-center lg:justify-end">
            <Image
              src={Goals}
              alt="UN SDG Goals"
              className="max-w-full h-auto"
            />
          </div>
        </div>
      </div>
      <div className="px-4 py-16">
        <div className="max-w-3xl mx-auto bg-white/80 dark:bg-slate-900/60 backdrop-blur-xl border border-gray-200 dark:border-slate-800 rounded-3xl p-8 md:p-12 shadow-2xl dark:shadow-none">
          <div className="text-center mb-10">
            <h2 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2">
              Analyze Your Project
            </h2>
          </div>

          <form onSubmit={handleFormSubmit} className="space-y-6">
            <div>
              <label
                htmlFor="projectName"
                className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2 text-left"
              >
                Project Name
                <span className="text-red-500 ml-1">*</span>
              </label>
              <input
                id="projectName"
                type="text"
                value={projectName}
                onChange={(e) => setProjectName(e.target.value)}
                placeholder="Enter your project name"
                required
                className="w-full bg-gray-50 dark:bg-slate-950/50 px-6 py-4 rounded-2xl border border-gray-200 dark:border-slate-700 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 dark:focus:ring-indigo-500/50 focus:border-transparent transition-all duration-200"
              />
            </div>

            <div>
              <label
                htmlFor="projectUrl"
                className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2 text-left"
              >
                Project GitHub URL
                <span className="text-red-500 ml-1">*</span>
              </label>
              <input
                id="projectUrl"
                type="url"
                value={projectUrl}
                onChange={(e) => setProjectUrl(e.target.value)}
                placeholder="https://github.com/username/repo"
                required
                className="w-full bg-gray-50 dark:bg-slate-950/50 px-6 py-4 rounded-2xl border border-gray-200 dark:border-slate-700 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 dark:focus:ring-indigo-500/50 focus:border-transparent transition-all"
              />
            </div>

            {/* Project Description */}
            <div>
              <label
                htmlFor="projectDescription"
                className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2 text-left"
              >
                SDG Relevance Description
                <span className="text-red-500 ml-1">*</span>
              </label>
              <textarea
                id="projectDescription"
                value={projectDescription}
                onChange={(e) => setProjectDescription(e.target.value)}
                placeholder="Please write a description of your project's relevance to the UN SDGs in around 100 to 120 words."
                required
                rows={12}
                className="w-full bg-gray-50 dark:bg-slate-950/50 px-6 py-4 rounded-2xl border border-gray-200 dark:border-slate-700 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 dark:focus:ring-indigo-500/50 focus:border-transparent transition-all"
              />
            </div>

            {/* Problem Statement */}
            {/* <div>
              <label
                htmlFor="problemStatement"
                className="block text-sm font-semibold text-gray-700 mb-2"
              >
                Problem Statement
                <span className="text-red-500 ml-1">*</span>
              </label>
              <textarea
                id="problemStatement"
                value={problemStatement}
                onChange={(e) => setProblemStatement(e.target.value)}
                placeholder="Describe the problem your project aims to solve"
                required
                className="w-full bg-white px-6 py-4 rounded-2xl border border-gray-200 text-gray-700 placeholder-gray-400 focus:outline-none  focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
              />
            </div> */}

            {/* Long Term Goal */}
            {/* <div>
              <label
                htmlFor="longTermGoal"
                className="block text-sm font-semibold text-gray-700 mb-2"
              >
                Long Term Goal
                <span className="text-red-500 ml-1">*</span>
              </label>
              <textarea
                id="longTermGoal"
                value={longTermGoal}
                onChange={(e) => setLongTermGoal(e.target.value)}
                placeholder="Describe the long term goal of your project"
                required
                className="w-full bg-white px-6 py-4 rounded-2xl border border-gray-200 text-gray-700 placeholder-gray-400 focus:outline-none  focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
              />
            </div> */}

            {/* Solution Approach */}
            {/* <div>
              <label
                htmlFor="solutionApproach"
                className="block text-sm font-semibold text-gray-700 mb-2"
              >
                Solution Approach
                <span className="text-red-500 ml-1">*</span>
              </label>
              <textarea
                id="solutionApproach"
                value={solutionApproach}
                onChange={(e) => setSolutionApproach(e.target.value)}
                placeholder="Describe your solution approach"
                required
                className="w-full bg-white px-6 py-4 rounded-2xl border border-gray-200 text-gray-700 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
              />
            </div> */}

            {/* Target Audience */}
            {/* <div>
              <label
                htmlFor="targetAudience"
                className="block text-sm font-semibold text-gray-700 mb-2 "
              >
                Target Audience
                <span className="text-red-500 ml-1">*</span>
              </label>
              <textarea
                id="targetAudience"
                value={targetAudience}
                onChange={(e) => setTargetAudience(e.target.value)}
                placeholder="Describe your target audience"
                required
                className="w-full bg-white px-6 py-4 rounded-2xl border border-gray-200 text-gray-700 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
              />
            </div> */}

            {/* Upload Message */}
            {uploadMsg && (
              <div
                className={`p-4 rounded-2xl ${
                  uploadMsg.includes("success")
                    ? "bg-green-50  border border-green-200 "
                    : "bg-red-50 text-red-700 border border-red-200"
                }`}
              >
                <div className="flex items-center gap-2">
                  {uploadMsg.includes("success") ? (
                    <div className="w-5 h-5 bg-green-500 rounded-full flex items-center justify-center">
                      <TiTick className="w-5 h-5 text-white" />
                    </div>
                  ) : (
                    <div className="w-5 h-5 bg-red-500 rounded-full flex items-center justify-center">
                      <ImCross className="w-3 h-3 text-white" />
                    </div>
                  )}
                  <span className="font-medium">{uploadMsg}</span>
                </div>
              </div>
            )}
            {/* Submit Button */}
            <button
              type="submit"
              disabled={isUploading || !projectName || !projectUrl}
              className="w-full px-8 py-4 bg-indigo-600 hover:bg-indigo-700 dark:bg-indigo-500/90 dark:hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold rounded-2xl transition-all duration-300 shadow-md hover:shadow-lg transform hover:-translate-y-0.5"
            >
              {isUploading ? (
                <span className="flex items-center justify-center gap-2">
                  <AiOutlineLoading3Quarters className="animate-spin h-5 w-5" />
                  Processing...
                </span>
              ) : (
                "Analyze SDG Alignment"
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default MainScreen;
