"""
test_ensemble_endpoint.py

Tests http://127.0.0.1:5000/api/classify_st_url (GE-Lab + mpnet ensemble)
against the same 73-project set used for the Aurora-alone eval, so the
two are directly comparable before any merge logic gets built.

Reuses project lists already written — no retyping:
  - NEGATIVE_PROJECTS, POSITIVE_PROJECTS_SINGLE_SDG from test_aurora_alone.py
  - POSITIVE_PROJECTS_BATCH2 from positive_projects_batch2.py

Computes the practical starting metric set:
  1. Macro-F1 (precision/recall per SDG, averaged across SDGs that appear)
  2. Negative-set false-positive rate
  3. Ground-truth labels caught (direct overlap count, not Jaccard)
"""

import requests
import time
import re
from collections import defaultdict

from eval.Positive_projects import Positive_projects, Negetive_projects


ST_URL_ENDPOINT = "http://127.0.0.1:5000/api/classify_st_url"

ALL_POSITIVES = Positive_projects
NEGATIVE_PROJECTS = Negetive_projects

def hit_st_url(project: dict) -> dict:
    payload = {
        "projectName":        project["projectName"],
        "projectUrl":         project["projectUrl"],
        "projectDescription": project["projectDescription"],
    }
    r = requests.post(ST_URL_ENDPOINT, json=payload, timeout=120)

    r.raise_for_status()
    return r.json()


def extract_predicted_sdg_numbers(predictions: list[dict]) -> set[int]:
    nums = set()
    for p in predictions:
        match = re.match(r"SDG\s*(\d+)", p.get("sdg", ""))
        if match:
            nums.add(int(match.group(1)))
    return nums


def main():
    # per-SDG counts for macro-F1 (1..17)
    tp = defaultdict(int)   # predicted AND true
    fp = defaultdict(int)   # predicted, NOT true
    fn = defaultdict(int)   # true, NOT predicted

    false_positive_count = 0
    negative_total = 0

    exact_or_overlap_hits = 0
    ground_truth_total = 0
    total_true_labels = 0      # total individual ground-truth SDG labels across all projects
    total_true_labels_caught = 0  # how many of those individual labels the prediction actually caught

    # print("=== NEGATIVE PROJECTS (ensemble endpoint) ===")
    # for proj in NEGATIVE_PROJECTS:
    #     print(f"\n--- {proj['projectName']} ---")
    #     try:
    #         response = hit_st_url(proj)
    #     except Exception as exc:
    #         print(f"  FAILED: {exc}")
    #         continue

    #     predicted = extract_predicted_sdg_numbers(response.get("predictions", []))
    #     print(f"  predicted: {predicted}")

    #     negative_total += 1
    #     if predicted:
    #         false_positive_count += 1
    #         print(f"  ✗ FALSE POSITIVE")
    #     else:
    #         print(f"  ✓ correctly empty")

    #     # every predicted label on a true-negative project is a false positive
    #     for sdg in predicted:
    #         fp[sdg] += 1

    #     time.sleep(10)  # stay under RPM cap

    print("\n\n=== POSITIVE PROJECTS (ensemble endpoint, ground truth check) ===")
    for proj in ALL_POSITIVES:
        gt = set(proj["ground_truth_sdgs"])
        print(f"\n--- {proj['projectName']} (ground truth: {gt}) ---")
        try:
            response = hit_st_url(proj)
        except Exception as exc:
            print(f"  FAILED: {exc}")
            continue

        predicted = extract_predicted_sdg_numbers(response.get("predictions", []))
        print(f"  predicted: {predicted}")

        ground_truth_total += 1
        overlap = predicted & gt
        caught = len(overlap)
        total_true_labels += len(gt)
        total_true_labels_caught += caught

        if overlap:
            exact_or_overlap_hits += 1
            print(f"  ✓ MATCH — caught {caught}/{len(gt)} ground-truth label(s): {overlap}")
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
        recall    = t / (t + f_n) if (t + f_n) else None
        if precision is not None and recall is not None and (precision + recall) > 0:
            f1 = 2 * precision * recall / (precision + recall)
        else:
            f1 = 0.0 if (t + f_p + f_n) > 0 else None  # None = SDG never appeared, skip

        if f1 is not None:
            f1_scores.append(f1)
            print(f"  SDG{sdg:<3} tp={t} fp={f_p} fn={f_n}  "
                  f"precision={precision if precision is not None else 'n/a'}  "
                  f"recall={recall if recall is not None else 'n/a'}  f1={f1:.2f}")

    macro_f1 = sum(f1_scores) / len(f1_scores) if f1_scores else 0.0

    print("\n--- SUMMARY ---")
    print(f"Macro-F1 (across {len(f1_scores)} SDGs with activity): {macro_f1:.3f}")
    print(f"Negative false-positive rate: {false_positive_count}/{negative_total} "
          f"({false_positive_count/negative_total:.1%})" if negative_total else "n/a")
    print(f"Projects with at least one correct SDG: {exact_or_overlap_hits}/{ground_truth_total} "
          f"({exact_or_overlap_hits/ground_truth_total:.1%})" if ground_truth_total else "n/a")
    print(f"Individual ground-truth labels caught: {total_true_labels_caught}/{total_true_labels} "
          f"({total_true_labels_caught/total_true_labels:.1%})" if total_true_labels else "n/a")

    print("\nCompare directly against Aurora-alone results from test_aurora_alone.py "
          "before deciding on merge logic.")


if __name__ == "__main__":
    main()