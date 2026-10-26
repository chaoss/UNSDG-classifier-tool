# SDG Classification Results: Analysis and Threshold Candidates

## Scope and data layout

The analysis notebook is [`classification_metrics_thresholds.ipynb`](./classification_metrics_thresholds.ipynb). It reads the source labels and saved classifier results directly from `backend/csv_data_per_sdg/`; rerun it after updating those files to refresh the metrics.

The 17 source files (`sdg_1.csv` through `sdg_17.csv`) contain project metadata, a `target_sdg` field, and binary ground-truth columns `sdg_1` through `sdg_17`. The 17 files in `res_per_sdg/` instead contain one row for each returned prediction, keyed back to the input by `source_file` and `source_row`, with the predicted SDG and score. The result writer persists only predictions returned by the endpoint; it does not write a complete 17-score vector or a status row for requests with no predictions.

The ST URL classification path uses a relevance check before inference and selects scores at or above `0.3`. The scores returned by the classifier are an ensemble: 40% zero-shot classifier score and 60% embedding similarity score after clipping/rescaling. These are ranking scores, not demonstrated calibrated probabilities.

## Executive findings

- The source files contain **486 input rows but only 204 normalized repository URLs**. There are 123 repository URLs repeated across source rows (up to 11 rows for one URL). The repeated entries have consistent ground-truth vectors, but many repeated runs have different saved scores.
- **302/486 request rows (62.1%)** have at least one saved prediction; these represent **144/204 unique repositories (70.6%)**. The remaining 184 request rows have no saved output. They may represent relevance-gated empty responses, no scores above the cutoff, or skipped failures; the result files do not record which.
- The result files contain **1,875 scores** out of 8,262 possible request/SDG cells (22.7%). A missing score on a request that has other saved scores only establishes that the score was below `0.3`; a wholly absent request cannot be interpreted as 17 negative predictions.
- At the current `0.3` cutoff, conditional (score-bearing requests only) weighted micro precision/recall/F1 are **0.304 / 0.752 / 0.433**; macro precision/recall/F1 are **0.304 / 0.747 / 0.414**. Weighted 17-label exact-match accuracy is **8.7%**.
- The per-SDG F1-maximizing candidates below raise apparent conditional weighted micro F1 to **0.515** and macro F1 to **0.507**, with micro precision **0.431** and recall **0.639**. Exact-match accuracy changes only to **9.0%**. These are in-sample results, not an unbiased estimate of future performance.
- The most evident weaknesses are low precision for many goals at `0.3`, poor results that remain after tuning for SDGs 6, 8, 9, 10, and 17, sparse positive support for SDGs 7, 14, and 15, substantial no-output coverage gaps, and score variation across repeated runs for the same repository.

## Metrics and threshold selection

The table reports per-category metrics conditional on the 144 unique repositories with at least one score-bearing request. Repeated score-bearing requests for the same normalized URL are retained to expose pipeline output variation, but each repository has a total weight of one (`1 / number of its score-bearing requests`). Positive support is the number of unique repositories with that ground-truth label in this score-bearing subset.

The candidate cutoff maximizes weighted F1 over a `0.01` grid from `0.30` to `0.99`; ties prefer higher precision and then the higher threshold. The table's candidate F1 is optimized on the same observations on which it is measured and is therefore optimistic.

| SDG | Positive repos | Current P / R / F1 (`0.30`) | Candidate cutoff | Candidate P / R / F1 | Candidate accuracy |
|---:|---:|---:|---:|---:|---:|
| 1 | 16 | 0.246 / 0.848 / 0.381 | **0.76** | 0.735 / 0.510 / 0.602 | 0.925 |
| 2 | 10 | 0.140 / 1.000 / 0.246 | **0.72** | 0.398 / 0.561 / 0.465 | 0.910 |
| 3 | 56 | 0.645 / 0.946 / 0.767 | **0.71** | 0.893 / 0.822 / 0.856 | 0.892 |
| 4 | 23 | 0.361 / 0.737 / 0.484 | **0.70** | 0.768 / 0.580 / 0.661 | 0.905 |
| 5 | 13 | 0.238 / 0.412 / 0.302 | **0.72** | 0.711 / 0.284 / 0.406 | 0.925 |
| 6 | 9 | 0.116 / 0.922 / 0.207 | **0.72** | 0.203 / 0.317 / 0.248 | 0.880 |
| 7 | 4 | 0.134 / 0.611 / 0.220 | **0.68** | 0.246 / 0.556 / 0.341 | 0.940 |
| 8 | 18 | 0.222 / 0.561 / 0.318 | **0.37** | 0.246 / 0.561 / 0.342 | 0.730 |
| 9 | 39 | 0.309 / 0.681 / 0.425 | **0.30** | 0.309 / 0.681 / 0.425 | 0.502 |
| 10 | 15 | 0.177 / 0.633 / 0.276 | **0.33** | 0.181 / 0.633 / 0.282 | 0.664 |
| 11 | 18 | 0.278 / 0.822 / 0.415 | **0.66** | 0.430 / 0.651 / 0.518 | 0.848 |
| 12 | 9 | 0.253 / 0.635 / 0.362 | **0.68** | 0.531 / 0.481 / 0.505 | 0.941 |
| 13 | 18 | 0.397 / 0.784 / 0.527 | **0.63** | 0.540 / 0.685 / 0.604 | 0.888 |
| 14 | 2 | 0.391 / 1.000 / 0.562 | **0.88** | 1.000 / 0.500 / 0.667 | 0.993 |
| 15 | 7 | 0.424 / 0.786 / 0.551 | **0.91** | 0.815 / 0.629 / 0.710 | 0.975 |
| 16 | 39 | 0.607 / 0.719 / 0.658 | **0.31** | 0.607 / 0.719 / 0.658 | 0.798 |
| 17 | 23 | 0.230 / 0.600 / 0.333 | **0.30** | 0.230 / 0.600 / 0.333 | 0.615 |

Accuracy is included for completeness, but can look deceptively high when negatives dominate. For example, the SDG 14 candidate accuracy is 0.993 despite only two positive repositories in the evaluated subset. Prefer precision, recall, F1, support, and exact-match accuracy together.

### Aggregate scores

| Operating point | Macro P / R / F1 / accuracy | Micro P / R / F1 | 17-label exact-match accuracy |
|---|---|---|---:|
| One `0.30` cutoff | 0.304 / 0.747 / 0.414 / 0.744 | 0.304 / 0.752 / 0.433 | 8.7% |
| Per-SDG candidates above | 0.520 / 0.575 / 0.507 / 0.843 | 0.431 / 0.639 / 0.515 | 9.0% |

The per-category cutoffs mostly exchange recall for precision. SDGs 9 and 17 retain `0.30`; SDG 16 moves only to `0.31`. This indicates that threshold adjustment alone does not resolve weak separation for those categories. SDG 6 also remains weak at its candidate cutoff (precision 0.203, F1 0.248). SDGs 7, 14, and 15 have only 4, 2, and 7 positive unique repositories respectively, so their apparently strong candidate results are especially unstable.

## Reliability and pipeline weaknesses

### Coverage and evaluation censoring

The score results are conditional on having at least one persisted prediction. Because the ST endpoint can stop before inference when its relevance assessment says text is not relevant, and the CSV runner skips failed HTTP responses, no-output rows cannot be assigned a trustworthy score or cause from these exports. This means the metrics do not measure end-to-end success or recall over all 204 repositories.

Within score-bearing requests, omitted SDG columns are known only to be below the existing `0.3` cutoff. The notebook never fills them with a score of zero and never treats a request with no saved scores as a valid all-negative example. Full-range ROC/PR curves, AUROC, average precision, calibration/Brier score, and end-to-end error rates cannot be recovered from the current output format.

### Repeated repository results vary

Although repeated URLs have consistent ground-truth vectors, **443/444 (99.8%)** of the repeated repository-SDG pairs with at least two observed saved scores have differing score values. Across the 73 repositories with multiple score-bearing runs, **176/1,241 (14.2%)** of repeated repository-SDG decisions differ at the current `0.3` cutoff; **140/1,241 (11.3%)** still differ at the candidate cutoffs.

This is direct evidence that one saved result may not be a stable representation of a repository. The CSVs do not preserve the generated summary, complete raw scores, or model/run version, so they do not identify the stage responsible for this variation. Capture those values before attributing it to the model, embeddings, summarization, or changing inputs.

### Category-level weaknesses

- At `0.3`, only SDGs 3 and 16 have precision above 0.5. The candidate cutoffs improve precision for most classes, but often reduce recall; they do not make an unreliable category dependable by themselves.
- SDG 6 has very low precision before and after tuning. SDGs 8, 9, 10, and 17 also have low candidate precision/F1 and are weak points for further error review.
- SDG 3 is the strongest supported class in this subset (56 positives; candidate F1 0.856). SDG 4, 13, and 15 also show useful candidate F1, but SDG 15 has only 7 positive repositories.
- Exact-match accuracy is under 9% at both operating points. A high score for one or several relevant SDGs should not be interpreted as a reliably correct full 17-label assignment.

## Recommendations

1. **Do not deploy the candidate cutoffs from this document as calibrated production thresholds.** Keep them as experiment values until evaluation on a repository-disjoint holdout supports them.
2. Create a reviewed, repository-deduplicated test set with multiple human annotations or adjudicated multi-label ground truth. Use grouped/nested cross-validation for threshold selection and reserve untouched repositories for final metrics.
3. Save one structured evaluation record per request, including status/error, relevance-gate outcome, input and generated summary, model/version, all 17 unfiltered scores, threshold configuration, and returned predictions. This makes no-output outcomes and score variation diagnosable.
4. Review false positives and false negatives for SDGs 6, 8, 9, 10, and 17; assess label definitions and training/evaluation data coverage before attempting further cutoff tuning.
5. Compare the zero-shot and embedding components separately, then compare the existing ensemble with alternative weights using the same grouped validation protocol. Do not infer component performance from the final ensemble scores alone.

## Reproducibility note

The notebook computes metrics from the CSVs present at execution time. The numeric findings above describe the current snapshot analyzed for this document; regenerated or revised inputs/results can change the counts, thresholds, and metrics. No classifier code or live serving thresholds are changed by this analysis.
