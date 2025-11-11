import React, { useState } from "react";
import Goals from "@/assets/UNSDG Goals Image.jpg";
import Image from "next/image";
import axios from "axios";
// import { SlCloudUpload } from "react-icons/sl";
import { TiTick } from "react-icons/ti";
import { ImCross } from "react-icons/im";
import { AiOutlineLoading3Quarters } from "react-icons/ai";

const MainScreen: React.FC<{
  setResults: React.Dispatch<React.SetStateAction<string | null>>;
}> = ({ setResults }) => {
  // const fileInputRef = useRef<HTMLInputElement>(null);
  // const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadMsg, setUploadMsg] = useState<string | null>(null);

  const [projectName, setProjectName] = useState("");
  const [projectUrl, setProjectUrl] = useState("");
  const [problemStatement, setProblemStatement] = useState("");
  const [longTermGoal, setLongTermGoal] = useState("");
  const [solutionApproach, setSolutionApproach] = useState("");
  const [targetAudience, setTargetAudience] = useState("");

  // const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
  //   const file = e.target.files?.[0] || null;
  //   setSelectedFile(file);
  //   setUploadMsg(null);
  // };

  const handleFormSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    // handleInteract();
    // if (!selectedFile) {
    //   setUploadMsg("Please upload an SDG.md file before submitting.");
    //   return;
    // }

    if (
      !projectName ||
      !projectUrl ||
      !problemStatement ||
      !longTermGoal ||
      !solutionApproach ||
      !targetAudience
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
      problemStatement: problemStatement,
      longTermGoal: longTermGoal,
      solutionApproach: solutionApproach,
      targetAudience: targetAudience,
    };
    // const formData = new FormData();
    // formData.append("project_name", projectName);
    // formData.append("project_url", projectUrl);
    // if (selectedFile) {w
    //   formData.append("file", selectedFile);
    // }

    try {
      setIsUploading(true);
      setUploadMsg(null);
      const base = "http://127.0.0.1:5000/";
      const response = await axios.post(base + "api/classify", finalizedData, {
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.statusText || response.statusText !== "OK") {
        throw new Error(response.data.error);
      }
      if (response.data && response.data.repo_url) {
        setUploadMsg("Text Analyzing Successfully!");
      }

      console.log("API Response:", response.data);
      setResults(response.data);
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

            {/* Problem Statement */}
            <div>
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
            </div>

            {/* Long Term Goal */}
            <div>
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
            </div>

            {/* Solution Approach */}
            <div>
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
            </div>

            {/* Target Audience */}
            <div>
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
            </div>

            {/* File Upload */}
            {/* <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                SDG.md file
                <span className="text-red-500 ml-1">*</span>
              </label>

              <div className="relative">
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".md, text/markdown"
                  onChange={handleFileChange}
                  className="hidden"
                />
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  disabled={isUploading}
                  className="w-full bg-white  px-6 py-4 border-2 border-dashed border-gray-300 rounded-2xl hover:border-purple-500 hover:bg-purple-50 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 text-left flex items-center justify-between"
                >
                  <span className="text-gray-600">
                    {selectedFile ? (
                      <span className="flex items-center gap-2">
                        <SlCloudUpload className="w-5 h-5 text-purple-600" />
                        <span className="font-medium text-purple-700">
                          {selectedFile.name}
                        </span>
                      </span>
                    ) : (
                      "Click to upload your SDG.md file"
                    )}
                  </span>

                  <SlCloudUpload className="w-5 h-5 text-gray-400" />
                </button>
              </div>

              {selectedFile && (
                <p className="mt-2 text-sm text-gray-500">
                  File size: {(selectedFile.size / 1024).toFixed(2)} KB
                </p>
              )}
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
