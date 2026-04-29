import React from "react";
import { RawResultsProps } from "@/types/main";

/*
RawResults Component
- Displays raw JSON results from SDG analysis
- Useful for debugging and transparency
*/

const RawResults: React.FC<RawResultsProps> = ({ results }) => {
  return (
    <div className="bg-white dark:bg-slate-900 border border-transparent dark:border-slate-800 rounded-xl p-6 shadow-lg dark:shadow-none">
      <h4 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-2">Raw Results:</h4>
      <pre className="bg-gray-100 dark:bg-slate-950 text-gray-800 dark:text-gray-300 rounded-lg p-4 overflow-auto text-sm">
        {JSON.stringify(results, null, 2)}
      </pre>
    </div>
  );
};

export default RawResults;
