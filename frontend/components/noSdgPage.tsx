import React from "react";
import { ArrowRight, Check, Clipboard, Compass, X } from "lucide-react";
import { Recommendation } from "@/types/main";

interface NoSdgPageProps {
  recommendation?: Recommendation;
}

const reasonMessages: Record<string, string> = {
  text_too_short: "Your project description and README are too short to assess SDG relevance.",
  no_sdg_signals: "No SDG-relevant signals were found in the provided text.",
  heavily_technical: "The description appears heavily technical without clear real-world impact signals.",
  threshold_too_high: "The text shows some SDG-relevant signals, but the project context may need more detail.",
  signals_present_but_low_similarity: "SDG-relevant signals were found, but similarity scores are low.",
};

const reasonDescriptions: Record<string, string> = {
  text_too_short: "Expand your project description to at least 20-30 words including what problem your project solves.",
  no_sdg_signals: "Make your description more elaborate and less technical. Focus on what the project does, who benefits, and the real-world impact.",
  heavily_technical: "Rewrite the description in non-technical terms. Remove mentions of programming languages, frameworks, and libraries. Focus on the problem your project addresses.",
  threshold_too_high: "Add specific details about your project's impact, beneficiaries, and real-world context.",
  signals_present_but_low_similarity: "Add more specific details about your project's impact, beneficiaries, and geographic or sector context.",
};

const NoSdgPage: React.FC<NoSdgPageProps> = ({ recommendation }) => {
  const [openModal, setOpenModal] = React.useState(false);
  const [copied, setCopied] = React.useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(guidance);
    setCopied(true);
  };

  const reason = recommendation
    ? reasonMessages[recommendation.reason] ||
      reasonDescriptions[recommendation.reason] ||
      "We couldn't find SDG matches above the relevance threshold."
    : "We couldn't find SDG matches above the relevance threshold for the provided repository/description.";

  const guidance = recommendation
    ? reasonDescriptions[recommendation.reason] || reason
    : "Describe the problem your project addresses, who benefits, and the real-world impact it aims to create.";

  const suggestions = recommendation?.suggestions.length
    ? recommendation.suggestions
    : [
        "Expand your project description to at least 20-30 words",
        "Include what problem your project solves",
        "Mention who benefits from your project",
        "Add geographic or sector context (e.g., 'rural farmers', 'low-income countries')",
      ];

  return (
    <section className="relative isolate overflow-hidden rounded-lg border border-[#b9def0] bg-[#f3faff] px-5 py-6 sm:px-8 sm:py-8">
      <div aria-hidden="true" className="pointer-events-none absolute -right-10 -top-12 h-48 w-48 rounded-full border-[24px] border-[#dceffa] sm:-right-5 sm:-top-16 sm:h-64 sm:w-64" />
      <div aria-hidden="true" className="pointer-events-none absolute right-8 top-8 h-24 w-24 rounded-full border border-[#c4e5f4] sm:right-16 sm:top-12 sm:h-32 sm:w-32" />

      <div className="relative max-w-3xl">
        <div className="mb-5 flex items-center gap-3">
          <span className="grid h-11 w-11 shrink-0 place-items-center rounded-full bg-[#009edb] text-white shadow-sm shadow-[#0079a8]/20">
            <Compass aria-hidden="true" size={22} strokeWidth={1.8} />
          </span>
          <div>
            <p className="text-xs font-bold uppercase text-[#0079a8]">UN Sustainable Development Goals</p>
            <p className="mt-0.5 text-sm font-medium text-[#4b6b7c]">Classification result</p>
          </div>
        </div>

        <h2 className="max-w-2xl text-2xl font-bold leading-tight text-[#123b56] sm:text-3xl">
          No SDG match found for this project
        </h2>
        <p className="mt-3 max-w-2xl text-base leading-7 text-[#426172]">{reason}</p>

        <div className="mt-7 border-t border-[#c8e3f0] pt-6">
          <div className="mb-4">
            <p className="text-lg font-semibold text-[#123b56]">Strengthen the project context</p>
            <p className="mt-1 text-sm text-[#567484]">A little more real-world detail can make its contribution clearer.</p>
          </div>
          <ul className="grid gap-3 sm:grid-cols-2">
            {suggestions.map((suggestion, index) => (
              <li key={`${suggestion}-${index}`} className="flex min-w-0 items-start gap-3 rounded-md border border-[#d6eaf4] bg-white/85 px-4 py-3">
                <span className="grid h-6 w-6 shrink-0 place-items-center rounded-full bg-[#e2f4fb] text-xs font-bold text-[#0079a8]">{String(index + 1).padStart(2, "0")}</span>
                <span className="text-sm leading-6 text-[#365566]">{suggestion}</span>
              </li>
            ))}
          </ul>
        </div>

        <button
          type="button"
          onClick={() => setOpenModal(true)}
          className="mt-6 inline-flex min-h-11 items-center gap-2 rounded-md bg-[#0079a8] px-5 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-[#005f86] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0079a8]"
        >
          Get detailed guidance <ArrowRight aria-hidden="true" size={17} />
        </button>
      </div>

      {openModal && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-[#082d43]/60 p-4 backdrop-blur-sm"
          onClick={() => setOpenModal(false)}
        >
          <div
            className="w-full max-w-lg rounded-lg border border-[#c7e1ee] bg-white p-6 shadow-2xl sm:p-8"
            role="dialog"
            aria-modal="true"
            aria-labelledby="guidance-title"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-xs font-bold uppercase text-[#0079a8]">Next steps</p>
                <h3 id="guidance-title" className="mt-2 text-xl font-bold text-[#123b56] sm:text-2xl">Make the impact easier to see</h3>
              </div>
              <button
                type="button"
                onClick={() => setOpenModal(false)}
                aria-label="Close guidance"
                className="grid h-9 w-9 shrink-0 place-items-center rounded-md text-[#557181] transition-colors hover:bg-[#edf7fb] hover:text-[#123b56] focus-visible:outline-2 focus-visible:outline-[#0079a8]"
              >
                <X aria-hidden="true" size={19} />
              </button>
            </div>
            <p className="mt-4 text-sm leading-6 text-[#4b6878]">{reason}</p>

            <div className="mt-6 rounded-md border border-[#c8e3f0] bg-[#f3faff] p-4">
              <p className="text-sm font-semibold text-[#23485d]">Suggested description focus</p>
              <p className="mt-2 text-sm leading-6 text-[#4b6878]">{guidance}</p>
            </div>

            <div className="mt-6 flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
              <button
                type="button"
                onClick={() => setOpenModal(false)}
                className="min-h-10 rounded-md border border-[#c8dce7] px-4 py-2 text-sm font-semibold text-[#355668] transition-colors hover:bg-[#f3f8fa]"
              >
                Close
              </button>
              <button
                type="button"
                onClick={handleCopy}
                className="inline-flex min-h-10 items-center justify-center gap-2 rounded-md bg-[#0079a8] px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-[#005f86]"
              >
                {copied ? <Check aria-hidden="true" size={16} /> : <Clipboard aria-hidden="true" size={16} />}
                {copied ? "Copied" : "Copy guidance"}
              </button>
            </div>
          </div>
        </div>
      )}
    </section>
  );
};

export default NoSdgPage;