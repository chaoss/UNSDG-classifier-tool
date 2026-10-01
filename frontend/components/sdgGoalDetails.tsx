"use client";

import { useEffect } from "react";
import Image, { type StaticImageData } from "next/image";
import { ChevronDown, X } from "lucide-react";
import goal1 from "../../backend/data/sdg_targets/goal_1.json";
import goal2 from "../../backend/data/sdg_targets/goal_2.json";
import goal3 from "../../backend/data/sdg_targets/goal_3.json";
import goal4 from "../../backend/data/sdg_targets/goal_4.json";
import goal5 from "../../backend/data/sdg_targets/goal_5.json";
import goal6 from "../../backend/data/sdg_targets/goal_6.json";
import goal7 from "../../backend/data/sdg_targets/goal_7.json";
import goal8 from "../../backend/data/sdg_targets/goal_8.json";
import goal9 from "../../backend/data/sdg_targets/goal_9.json";
import goal10 from "../../backend/data/sdg_targets/goal_10.json";
import goal11 from "../../backend/data/sdg_targets/goal_11.json";
import goal12 from "../../backend/data/sdg_targets/goal_12.json";
import goal13 from "../../backend/data/sdg_targets/goal_13.json";
import goal14 from "../../backend/data/sdg_targets/goal_14.json";
import goal15 from "../../backend/data/sdg_targets/goal_15.json";
import goal16 from "../../backend/data/sdg_targets/goal_16.json";
import goal17 from "../../backend/data/sdg_targets/goal_17.json";
import image1 from "../../sdg_goal_imgs/E-WEB-Goal-01.png";
import image2 from "../../sdg_goal_imgs/E-WEB-Goal-02.png";
import image3 from "../../sdg_goal_imgs/E-WEB-Goal-03.png";
import image4 from "../../sdg_goal_imgs/E-WEB-Goal-04.png";
import image5 from "../../sdg_goal_imgs/E-WEB-Goal-05.png";
import image6 from "../../sdg_goal_imgs/E-WEB-Goal-06.png";
import image7 from "../../sdg_goal_imgs/E-WEB-Goal-07.png";
import image8 from "../../sdg_goal_imgs/E-WEB-Goal-08.png";
import image9 from "../../sdg_goal_imgs/E-WEB-Goal-09.png";
import image10 from "../../sdg_goal_imgs/E-WEB-Goal-10.png";
import image11 from "../../sdg_goal_imgs/E-WEB-Goal-11.png";
import image12 from "../../sdg_goal_imgs/E-WEB-Goal-12.png";
import image13 from "../../sdg_goal_imgs/E-WEB-Goal-13.png";
import image14 from "../../sdg_goal_imgs/E-WEB-Goal-14.png";
import image15 from "../../sdg_goal_imgs/E-WEB-Goal-15.png";
import image16 from "../../sdg_goal_imgs/E-WEB-Goal-16.png";
import image17 from "../../sdg_goal_imgs/E-WEB-Goal-17.png";

type Indicator = {
  code: string;
  description: string;
  tier?: string | null;
};

type Target = {
  code: string;
  title: string;
  description?: string;
  indicators?: Indicator[];
};

type Goal = {
  title: string;
  description?: string;
  targets?: Target[];
};

type GoalDetailsProps = {
  sdgNumber: string;
  onClose: () => void;
};

const goalDetails: Record<
  number,
  { goal: Goal; image: StaticImageData; color: string }
> = {
  1: { goal: goal1[0] as Goal, image: image1, color: "#E5243B" },
  2: { goal: goal2[0] as Goal, image: image2, color: "#DDA63A" },
  3: { goal: goal3[0] as Goal, image: image3, color: "#4C9F38" },
  4: { goal: goal4[0] as Goal, image: image4, color: "#C5192D" },
  5: { goal: goal5[0] as Goal, image: image5, color: "#FF3A21" },
  6: { goal: goal6[0] as Goal, image: image6, color: "#26BDE2" },
  7: { goal: goal7[0] as Goal, image: image7, color: "#FCC30B" },
  8: { goal: goal8[0] as Goal, image: image8, color: "#A21942" },
  9: { goal: goal9[0] as Goal, image: image9, color: "#FD6925" },
  10: { goal: goal10[0] as Goal, image: image10, color: "#DD1367" },
  11: { goal: goal11[0] as Goal, image: image11, color: "#FD9D24" },
  12: { goal: goal12[0] as Goal, image: image12, color: "#BF8B2E" },
  13: { goal: goal13[0] as Goal, image: image13, color: "#3F7E44" },
  14: { goal: goal14[0] as Goal, image: image14, color: "#0A97D9" },
  15: { goal: goal15[0] as Goal, image: image15, color: "#56C02B" },
  16: { goal: goal16[0] as Goal, image: image16, color: "#00689D" },
  17: { goal: goal17[0] as Goal, image: image17, color: "#19486A" },
};

const SdgGoalDetails = ({ sdgNumber, onClose }: GoalDetailsProps) => {
  const details = goalDetails[Number(sdgNumber)];

  useEffect(() => {
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";

    const closeOnEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape") onClose();
    };

    window.addEventListener("keydown", closeOnEscape);
    return () => {
      document.body.style.overflow = previousOverflow;
      window.removeEventListener("keydown", closeOnEscape);
    };
  }, [onClose]);

  if (!details) return null;

  const targets = details.goal.targets ?? [];
  const indicatorCount = targets.reduce(
    (count, target) => count + (target.indicators?.length ?? 0),
    0,
  );

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/60 p-3 backdrop-blur-sm sm:p-6"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) onClose();
      }}
    >
      <section
        aria-labelledby="sdg-details-title"
        aria-modal="true"
        className="flex max-h-[94vh] w-full max-w-4xl flex-col overflow-hidden rounded-lg bg-white shadow-2xl"
        role="dialog"
      >
        <header
          className="relative flex shrink-0 items-center gap-4 p-4 text-white sm:gap-6 sm:p-6"
          style={{ backgroundColor: details.color }}
        >
          <Image
            src={details.image}
            alt={`Official artwork for Sustainable Development Goal ${sdgNumber}`}
            className="h-20 w-20 shrink-0 object-cover shadow-md sm:h-28 sm:w-28"
            priority
          />
          <div className="min-w-0 flex-1 pr-10">
            <p className="text-xs font-bold uppercase tracking-wide text-white/85">
              Goal {sdgNumber} · {targets.length} targets · {indicatorCount} indicators
            </p>
            <h2 id="sdg-details-title" className="mt-1 text-xl font-bold leading-tight sm:text-3xl">
              {details.goal.title}
            </h2>
          </div>
          <button
            type="button"
            aria-label="Close goal details"
            onClick={onClose}
            className="absolute right-3 top-3 inline-flex h-10 w-10 items-center justify-center rounded-full text-white transition hover:bg-black/15 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white"
          >
            <X size={22} aria-hidden="true" />
          </button>
        </header>

        <div className="min-h-0 overflow-y-auto">
          {details.goal.description && (
            <p className="border-b border-slate-200 px-5 py-4 text-sm leading-relaxed text-slate-700 sm:px-7">
              {details.goal.description}
            </p>
          )}

          <div className="grid gap-3 border-b border-slate-200 bg-slate-50 px-5 py-4 sm:grid-cols-2 sm:px-7">
            <div className="border-l-4 border-slate-700 pl-3">
              <p className="text-sm font-bold text-slate-900">Target</p>
              <p className="mt-1 text-sm leading-relaxed text-slate-600">
                A specific outcome the UN aims to achieve under this goal.
              </p>
            </div>
            <div className="border-l-4 border-slate-300 pl-3">
              <p className="text-sm font-bold text-slate-900">Indicator</p>
              <p className="mt-1 text-sm leading-relaxed text-slate-600">
                A measurable statistic used to track progress toward a target.
              </p>
            </div>
          </div>

          <div className="space-y-3 p-4 sm:p-6">
            {targets.map((target, index) => {
              const indicators = target.indicators ?? [];

              return (
                <details
                  key={target.code}
                  className="group overflow-hidden rounded-md border border-slate-200 bg-white open:border-slate-300"
                  open={index === 0}
                >
                  <summary className="flex cursor-pointer list-none items-start gap-3 p-4 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset sm:items-center">
                    <span
                      className="shrink-0 rounded px-2 py-1 text-sm font-bold text-white"
                      style={{ backgroundColor: details.color }}
                    >
                      {target.code}
                    </span>
                    <span className="min-w-0 flex-1 text-sm font-semibold leading-relaxed text-slate-800 sm:text-base">
                      {target.title}
                    </span>
                    <span className="hidden shrink-0 text-xs font-medium text-slate-500 sm:inline">
                      {indicators.length} {indicators.length === 1 ? "indicator" : "indicators"}
                    </span>
                    <ChevronDown
                      size={20}
                      aria-hidden="true"
                      className="mt-0.5 shrink-0 text-slate-500 transition-transform group-open:rotate-180 sm:mt-0"
                    />
                  </summary>

                  <div className="border-t border-slate-100 bg-slate-50/70 px-4 py-3 sm:px-5">
                    {indicators.length > 0 ? (
                      <ul className="space-y-2">
                        {indicators.map((indicator) => (
                          <li
                            key={indicator.code}
                            className="grid gap-1 rounded bg-white px-3 py-3 sm:grid-cols-[5.5rem_1fr_auto] sm:items-start sm:gap-3"
                          >
                            <span className="text-xs font-bold text-slate-500">
                              {indicator.code}
                            </span>
                            <span className="text-sm leading-relaxed text-slate-700">
                              {indicator.description}
                            </span>
                            {indicator.tier && (
                              <span className="w-fit rounded-full bg-slate-100 px-2 py-1 text-xs font-medium text-slate-600">
                                Tier {indicator.tier}
                              </span>
                            )}
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-sm text-slate-600">
                        No indicators are listed for this target.
                      </p>
                    )}
                  </div>
                </details>
              );
            })}
          </div>
        </div>
      </section>
    </div>
  );
};

export default SdgGoalDetails;