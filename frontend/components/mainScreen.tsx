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

    const trimmedName = projectName.trim();
    const trimmedUrl = projectUrl.trim();
    const trimmedDesc = projectDescription.trim();

    if (!trimmedName || !trimmedUrl || !trimmedDesc) {
      setUploadMsg("Please fill in all required fields before submitting.");
      return;
    }

    // GitHub URL validation regex
    const githubUrlRegex = /^https?:\/\/(www\.)?github\.com\/[\w.-]+\/[\w.-]+\/?$/;
    if (!githubUrlRegex.test(trimmedUrl)) {
      setUploadMsg("Please enter a valid GitHub repository URL (e.g., https://github.com/username/repository).");
      return;
    }

    const finalizedData = {
      projectName: trimmedName,
      projectUrl: trimmedUrl,
      projectDescription: trimmedDesc,
    };

    localStorage.setItem("projectDescription", trimmedDesc);
    localStorage.setItem("projectName", trimmedName);
    localStorage.setItem("projectUrl", trimmedUrl);

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
    } catch (error: any) {
      console.error("Error:", error);
      const backendError = error.response?.data?.message || error.response?.data?.error;
      const fallbackError = error.message === "Network Error" 
        ? "Network error: Unable to reach the server. Please try again later."
        : "Text Analyzing Failed. Please try again.";
      setUploadMsg(backendError || fallbackError);
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
      <div className="text-center px-8 py-16 bg-purple-400">
        <div className="max-w-3xl mx-auto">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold text-white mb-2">
              Analyze Your Project
            </h2>
          </div>

          <form onSubmit={handleFormSubmit} className="space-y-6">
            <div>
              <label
                htmlFor="projectName"
                className="block text-sm font-semibold text-gray-700 mb-2"
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
                className="w-full bg-white px-6 py-4 rounded-2xl border border-gray-200 text-gray-700 placeholder-gray-400 focus:outline-none focus:ring-purple-500 focus:border-transparent transition-all duration-200"
              />
            </div>

            <div>
              <label
                htmlFor="projectUrl"
                className="block text-sm font-semibold text-gray-700 mb-2"
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
                className="w-full bg-white px-6 py-4 rounded-2xl border border-gray-200 text-gray-700 placeholder-gray-400 focus:outline-none  focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
              />
            </div>

            {/* Project Description */}
            <div>
              <label
                htmlFor="projectDescription"
                className="block text-sm font-semibold text-gray-700 mb-2 "
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
                className="w-full bg-white px-6 py-4 rounded-2xl border border-gray-200 text-gray-700 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
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
              className="w-full px-8 py-4 bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold rounded-2xl transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
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
