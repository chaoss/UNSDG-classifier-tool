import React from "react";

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

type SDGData = {
  prediction: number;
  sdg: {
    "@type": string;
    code: string;
    icon: string;
    id: string;
    label: string;
    name: string;
    type: string;
  };
};

type SDGCardProps = {
  sdgKey: string;
  confidence: number;
};

type CardGridProps = {
  sdgPredictions: SDGData[] | Record<string, SDGValue>;
};

const SDGCard = ({ sdgKey, confidence }: SDGCardProps) => {
  // Extract SDG number and name
  const sdgMatch = sdgKey.match(/SDG (\d+): (.+)/);
  const sdgNumber = sdgMatch ? sdgMatch[1] : "";
  const sdgName = sdgMatch ? sdgMatch[2] : sdgKey;

  // Calculate confidence score and percentage
  const confidenceScore = Number(confidence);
  const confidencePercentage = Math.round(confidenceScore * 100);

  // Determine confidence level and colors
  let confidenceLevel = "";
  let colorClasses = "";
  let bgColor = "";

  if (confidenceScore >= 0.8) {
    confidenceLevel = "High";
    colorClasses = "text-green-700 border-green-300";
    bgColor = "bg-green-50";
  } else if (confidenceScore >= 0.6) {
    confidenceLevel = "Medium";
    colorClasses = "text-yellow-700 border-yellow-300";
    bgColor = "bg-yellow-50";
  } else {
    confidenceLevel = "Low";
    colorClasses = "text-red-700 border-red-300";
    bgColor = "bg-red-50";
  }

  return (
    <div
      className={`${bgColor} ${colorClasses} border rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow duration-200`}
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
            <span
              className={`text-xs px-2 py-1 rounded-full font-medium ${
                confidenceLevel === "High"
                  ? "bg-green-100 text-green-800"
                  : confidenceLevel === "Medium"
                  ? "bg-yellow-100 text-yellow-800"
                  : "bg-red-100 text-red-800"
              }`}
            >
              {confidenceLevel} Match
            </span>
          </div>
        </div>
        <div className="text-right">
          <div className="text-2xl font-bold text-gray-800">
            {confidencePercentage}%
          </div>
        </div>
      </div>

      {/* SDG Name */}
      <h5 className="font-medium text-gray-700 mb-3 leading-tight line-clamp-2">
        {sdgName}
      </h5>

      {/* Progress Bar */}
      <div className="space-y-2">
        <div className="flex justify-between text-sm text-gray-600">
          <span>Confidence Score</span>
          <span>{confidenceScore.toFixed(3)}</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className={`h-2 rounded-full transition-all duration-300 ${
              confidenceLevel === "High"
                ? "bg-green-500"
                : confidenceLevel === "Medium"
                ? "bg-yellow-500"
                : "bg-red-500"
            }`}
            style={{ width: `${confidencePercentage}%` }}
          ></div>
        </div>
      </div>
    </div>
  );
};

const CardGrid = ({ sdgPredictions }: CardGridProps) => {
  // Convert object to array if needed
  const predictionsArray: SDGData[] = Array.isArray(sdgPredictions)
    ? sdgPredictions
    : (Object.values(sdgPredictions)
        .filter((item) => item?.sdg && item.prediction > 0)
        .map((item) => ({
          prediction: item.prediction,
          sdg: {
            "@type": item.sdg["@type"] || "sdg",
            code: item.sdg.code || "",
            icon: item.sdg.icon || "",
            id: item.sdg.id || "",
            label: item.sdg.label || "",
            name: item.sdg.name || "",
            type: item.sdg.type || "Goal",
          },
        })) as SDGData[]);

  console.log("SDG Predictions:", predictionsArray);

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {/* Left container */}
      {/* A visual representation probably a Pie Chart or Donut Chart */}
      {/* Right container */}
      {predictionsArray
        .sort((a, b) => b.prediction - a.prediction)
        .map((item) => (
          <SDGCard
            key={item.sdg.code}
            sdgKey={`SDG ${item.sdg.code}: ${item.sdg.name}`}
            confidence={item.prediction}
          />
        ))}
    </div>
  );
};

export default CardGrid;
