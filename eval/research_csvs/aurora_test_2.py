"""
test_aurora_endpoint.py

Tests http://127.0.0.1:5000/api/classify_aurora (Aurora endpoint)
against the same 73-project set used for the ensemble eval, so the
two are directly comparable before any merge logic gets built.

Reuses project lists already written — no retyping:
  - NEGATIVE_PROJECTS
  - ALL_POSITIVES

Computes the practical starting metric set:
  1. Macro-F1 (precision/recall per SDG, averaged across SDGs that appear)
  2. Negative-set false-positive rate
  3. Ground-truth labels caught (direct overlap count, not Jaccard)
"""

import requests
import time
import re
from collections import defaultdict

from Positive_projects import Positive_projects, Negetive_projects


AURORA_ENDPOINT = "http://127.0.0.1:5000/api/classify_aurora"

ALL_POSITIVES = Positive_projects
NEGATIVE_PROJECTS = Negetive_projects


def hit_aurora(project: dict) -> dict:
    payload = {
        "projectName": project["projectName"],
        "projectUrl": project["projectUrl"],
        "projectDescription": project["projectDescription"],
    }

    r = requests.post(AURORA_ENDPOINT, json=payload, timeout=120)
    r.raise_for_status()
    return r.json()


def extract_predicted_sdg_numbers(sdg_predictions: dict) -> set[int]:
    nums = set()
    for key in sdg_predictions.keys():
        match = re.match(r"SDG\s*(\d+)", key)
        if match:
            nums.add(int(match.group(1)))
    return nums


def main():
    # per-SDG counts for macro-F1 (1..17)
    tp = defaultdict(int)
    fp = defaultdict(int)
    fn = defaultdict(int)

    false_positive_count = 0
    negative_total = 0

    exact_or_overlap_hits = 0
    ground_truth_total = 0
    total_true_labels = 0
    total_true_labels_caught = 0

    print("=== NEGATIVE PROJECTS (Aurora endpoint) ===")
    for proj in NEGATIVE_PROJECTS:
        print(f"\n--- {proj['projectName']} ---")
        try:
            response = hit_aurora(proj)
        except Exception as exc:
            print(f"  FAILED: {exc}")
            continue
    
        predicted = extract_predicted_sdg_numbers(
            response.get("sdg_predictions", {})
        )
        print(f"  predicted: {predicted}")
    
        negative_total += 1
    
        if predicted:
            false_positive_count += 1
            print("  ✗ FALSE POSITIVE")
        else:
            print("  ✓ correctly empty")
    
        for sdg in predicted:
            fp[sdg] += 1
    
        time.sleep(10)

    print("\n\n=== POSITIVE PROJECTS (Aurora endpoint, ground truth check) ===")

    for proj in ALL_POSITIVES:

        gt = set(proj["ground_truth_sdgs"])

        print(f"\n--- {proj['projectName']} (ground truth: {gt}) ---")

        try:
            response = hit_aurora(proj)
        except Exception as exc:
            print(f"  FAILED: {exc}")
            continue

        predicted = extract_predicted_sdg_numbers(
            response.get("sdg_predictions", {})
        )

        print(f"  predicted: {predicted}")

        ground_truth_total += 1

        overlap = predicted & gt
        caught = len(overlap)

        total_true_labels += len(gt)
        total_true_labels_caught += caught

        if overlap:
            exact_or_overlap_hits += 1
            print(
                f"  ✓ MATCH — caught {caught}/{len(gt)} ground-truth label(s): {overlap}"
            )
        else:
            print(f"  ✗ MISS — caught 0/{len(gt)} ground-truth label(s)")

        for sdg in gt:
            if sdg in predicted:
                tp[sdg] += 1
            else:
                fn[sdg] += 1

        for sdg in predicted:
            if sdg not in gt:
                fp[sdg] += 1

        time.sleep(10)

    # ── macro-F1 across all 17 SDGs ───────────────────────────────────────

    print("\n\n--- PER-SDG PRECISION / RECALL / F1 ---")

    f1_scores = []

    for sdg in range(1, 18):

        t, f_p, f_n = tp[sdg], fp[sdg], fn[sdg]

        precision = t / (t + f_p) if (t + f_p) else None
        recall = t / (t + f_n) if (t + f_n) else None

        if precision is not None and recall is not None and (precision + recall) > 0:
            f1 = 2 * precision * recall / (precision + recall)
        else:
            f1 = 0.0 if (t + f_p + f_n) > 0 else None

        if f1 is not None:
            f1_scores.append(f1)
            print(
                f"  SDG{sdg:<3} tp={t} fp={f_p} fn={f_n}  "
                f"precision={precision if precision is not None else 'n/a'}  "
                f"recall={recall if recall is not None else 'n/a'}  "
                f"f1={f1:.2f}"
            )

    macro_f1 = sum(f1_scores) / len(f1_scores) if f1_scores else 0.0

    print("\n--- SUMMARY ---")

    print(
        f"Macro-F1 (across {len(f1_scores)} SDGs with activity): {macro_f1:.3f}"
    )

    print(
        f"Negative false-positive rate: {false_positive_count}/{negative_total} "
        f"({false_positive_count/negative_total:.1%})"
        if negative_total
        else "n/a"
    )

    print(
        f"Projects with at least one correct SDG: "
        f"{exact_or_overlap_hits}/{ground_truth_total} "
        f"({exact_or_overlap_hits/ground_truth_total:.1%})"
        if ground_truth_total
        else "n/a"
    )

    print(
        f"Individual ground-truth labels caught: "
        f"{total_true_labels_caught}/{total_true_labels} "
        f"({total_true_labels_caught/total_true_labels:.1%})"
        if total_true_labels
        else "n/a"
    )

    print(
        "\nCompare directly against ensemble endpoint results "
        "before deciding on merge logic."
    )


if __name__ == "__main__":
    main()