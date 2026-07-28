"""
test_aurora_alone.py

Same 73-project test set (30 negative + 43 real DPGA/OpenSustain positive
with ground truth), but run through Aurora ALONE — no ensemble, no merge.
Purpose: get Aurora's standalone accuracy % to compare against ensemble's
73.3% baseline, so we know if Aurora is worth merging in at all before
building merge logic.

Calls aurora_api.main() directly (function call, not HTTP — Aurora
integration is a local import, not a separate running service).
"""

import time
import re
from aurora_api import main as aurora_classify

from eval.Positive_projects import Positive_projects, Negetive_projects

# ── same negative set as before ───────────────────────────────────────────

# ── original 31 positive (single-SDG, DPGA registry) ──────────────────────
# NOTE: import from your existing test_dpga_real_positives.py instead of
# retyping — shown inline here only for a fully standalone script.
# If you already have that file, replace this block with:
#   from test_dpga_real_positives import POSITIVE_PROJECT
# ── batch 2, multi-SDG, platform-diverse — import from the file already written ──


ALL_POSITIVES = Positive_projects
NEGATIVE_PROJECTS = Negetive_projects
print(f"\033[32m Loaded {len(ALL_POSITIVES)} positive projects for Aurora-alone test\033[0m\n")
def extract_predicted_sdg_numbers_from_aurora(sdg_predictions: dict) -> set[int]:
    """Aurora keys look like 'SDG 3: Good Health and Well-being'."""
    nums = set()
    for key in sdg_predictions.keys():
        match = re.match(r"SDG\s*(\d+)", key)
        if match:
            nums.add(int(match.group(1)))
    return nums


def main():
    ground_truth_hits = 0
    ground_truth_total = 0
    false_positive_count = 0
    negative_total = 0

    print("=== NEGATIVE PROJECTS (Aurora alone) ===")
    for proj in NEGATIVE_PROJECTS:
        print(f"\n--- {proj['projectName']} ---")
        result = aurora_classify(
            text=proj["projectDescription"],
            project_name=proj["projectName"],
            project_url=proj["projectUrl"],
        )
        if "error" in result:
            print(f"  FAILED: {result.get('message')} — {result.get('error')}")
            continue

        predicted = extract_predicted_sdg_numbers_from_aurora(result.get("sdg_predictions", {}))
        print(f"  predicted SDGs: {predicted}  |  raw: {result.get('sdg_predictions')}")
        negative_total += 1
        if predicted:
            false_positive_count += 1
            print(f"  ✗ FALSE POSITIVE — should be empty, got {predicted}")
        else:
            print(f"  ✓ correctly empty")
        time.sleep(2)

    print("\n\n=== POSITIVE PROJECTS (Aurora alone, ground truth check) ===")
    for proj in ALL_POSITIVES:
        gt = set(proj["ground_truth_sdgs"])
        print(f"\n--- {proj['projectName']} (ground truth: {gt}) ---")
        result = aurora_classify(
            text=proj["projectDescription"],
            project_name=proj["projectName"],
            project_url=proj["projectUrl"],
        )
        if "error" in result:
            print(f"  FAILED: {result.get('message')} — {result.get('error')}")
            continue

        predicted = extract_predicted_sdg_numbers_from_aurora(result.get("sdg_predictions", {}))
        print(f"  predicted SDGs: {predicted}  |  raw: {result.get('sdg_predictions')}")

        ground_truth_total += 1
        overlap = predicted & gt
        if overlap:
            ground_truth_hits += 1
            print(f"  ✓ MATCH — overlap: {overlap}")
        else:
            print(f"  ✗ MISS — no overlap with ground truth")
        time.sleep(1.5)

    print("\n\n--- AURORA-ALONE SUMMARY ---")
    print(f"Positive ground-truth accuracy: {ground_truth_hits}/{ground_truth_total} "
          f"({ground_truth_hits/ground_truth_total:.1%})" if ground_truth_total else "n/a")
    print(f"Negative false-positive rate: {false_positive_count}/{negative_total} "
          f"({false_positive_count/negative_total:.1%})" if negative_total else "n/a")
    print(f"\nCompare against ensemble baseline: 22/30 (73.3%) ground-truth accuracy.")


if __name__ == "__main__":
    main()