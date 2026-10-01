# Recommendation Pipeline

## 1. Purpose

The recommendation pipeline is a diagnostic helper for a classification run that returns no SDG predictions above the backend's output cutoff. It tries to explain why the available project text may not have produced a match and offers suggestions for improving that text.

It is implemented in `backend/services/recommendation_pipeline.py` as `assess_relevance(user_description, readme_text)`. It is not the main SDG classifier, does not choose or change the classifier's scores, and does not make a final determination that a project does or does not contribute to an SDG. The name "judge" is useful only in the limited sense that it applies a set of rules to diagnose an empty result. Its verdict concerns the evidence available in the submitted text, not the project's actual impact.

The recommendation code itself does not call an LLM. When the repository classifier is used, however, it may receive a summary that was produced by the separate Groq-based summarizer or by that summarizer's fallback logic.

## 2. End-to-end flow

1. The user enters a project name, repository URL, and project description in the frontend.
2. `frontend/components/mainScreen.tsx` sends both classification requests concurrently:
   - `POST /api/classify_st_url` for repository/README analysis.
   - `POST /api/classify_aurora` for Aurora classification.
3. The frontend prefers the repository/README response. It waits up to 120 seconds for that request; if it fails or times out, it waits for the Aurora request instead. The Aurora request is started even while the preferred request is running.
4. The selected backend route performs its classifier and filters the predictions. Both routes keep only scores strictly greater than `0.3`.
5. After classification succeeds, the route calls `assess_relevance` with the project description and a second text value, then attaches a recommendation only if the filtered predictions list is empty.
6. The frontend stores the selected route's response and renders the results view. If its `predictions` are empty, `frontend/components/results.tsx` renders `NoSdgPage` and passes it the optional recommendation.

The recommendation is therefore a post-classification explanation for an empty, filtered prediction list. It does not run before classification and does not decide whether an already-returned prediction is shown.

### Important paths that bypass the recommendation

- `/api/classify_st_url` returns early with an empty predictions list and a message if no repository URL is provided. This early response does not call `assess_relevance` and has no recommendation. The current frontend form normally requires a repository URL, but the backend route supports this separate case.
- If a route returns one or more predictions above `0.4`, its `recommendation` field is `null`, even when the recommendation scorer might have found weak text signals.
- If classification fails with an HTTP error, the route returns its error response rather than a recommendation result.
- In the frontend, the ST URL response is preferred. If it succeeds with no predictions, its recommendation is shown; the concurrently started Aurora response is not substituted just because its predictions might differ.

## 3. Text given to the assessor

The route inputs differ slightly:

| Route | `user_description` | `readme_text` |
|---|---|---|
| Aurora | User's submitted project description | `aurora_result.get("project_description", "")`, if present; otherwise empty |
| ST URL | User's submitted project description | The classifier's `summary`; if absent, repository metadata description; otherwise empty |

The current `aurora_api.main()` response does not set a `project_description` property. Consequently, the Aurora route normally assesses the submitted description alone.

The ST URL path fetches repository metadata, topics, and README text. `fetch_repo_text()` gives the user's submitted description priority over the repository's metadata description, then passes that description and repository content to `summarize_for_sdg()`. That summarizer can call Groq when configured, or return a fallback made from the name, description, topics, and failure reason. The resulting summary is passed to `assess_relevance` as `readme_text`. The submitted description can therefore appear both as the first argument and inside the second argument's summary.

## 4. Text cleaning and early length check

`_clean_text()` applies the same basic cleanup to each input:

- Strips leading and trailing whitespace.
- Collapses runs of spaces and tabs to one space.
- Reduces three or more consecutive newlines to two.
- Removes bare `http://` and `https://` URLs, including the non-whitespace text following them.

The assessor combines the cleaned strings with a space:

```text
combined = cleaned_description + " " + cleaned_readme
```

It counts words using whitespace splitting. If the combined text has fewer than **20 words**, it immediately returns `text_too_short`. The helper `_is_too_short()` has a default minimum of 15 words, but `assess_relevance()` explicitly calls it with `min_words=20`, so 20 is the effective threshold here. Exactly 20 words passes this check.

This length test uses both inputs. It is a count, not a measure of distinct information, readability, or coverage of the SDGs.

## 5. Signal detection

If the combined text is long enough, `_has_sdg_signals()` searches its lowercase, cleaned form in this order:

1. **Explicit SDG-related terms:** `sdg`, `sustainable development`, `goal`, `goal 1`, or `goal 2`. These are substring checks; for example, the broad word `goal` can match text without naming a particular SDG.
2. **Domain vocabulary:** any keyword in one of these groups:
   - Health: `health`, `medical`, `hospital`, `patient`, `clinical`
   - Education: `education`, `learning`, `school`, `student`, `teaching`
   - Environment: `environment`, `climate`, `ecological`, `sustainability`
   - Water: `water`, `sanitation`, `hygiene`, `wash`
   - Energy: `energy`, `power`, `electricity`, `renewable`
   - Agriculture: `agriculture`, `farm`, `farming`, `crop`, `rural`
   - Governance: `governance`, `policy`, `government`, `policy`
   - Gender: `gender`, `women`, `equality`, `female`
3. **Problem or beneficiary language:** `problem`, `solution`, `beneficiaries`, `users`, `impact`, `helps`, `addresses`, `reduces`, or `improves`.
4. **Heavily technical text check:** if none of the above matched, the code counts how many terms from this list occur as substrings: `python`, `javascript`, `react`, `api`, `database`, `framework`, `library`, `container`, `docker`, `cls`, `function`, `import`, `class`, `module`. It divides the number of matching terms by total whitespace-separated words. A ratio strictly greater than `0.5` returns the `heavily_technical` signal category.
5. Otherwise, no signal is found.

The category is selected by the first matching step. These are simple keyword checks, not language understanding: they do not account for negation, context, whether a claim is supported, or whether the terms refer to the project's real-world impact.

## 6. Embedding similarity and scoring

The assessor uses the process-wide embedder from `backend/services/embedder.py` only when the keyword scan has found a signal. The model is `sentence-transformers/all-mpnet-base-v2`, loaded lazily on first use and then reused within the process.

For a signal-positive input, the assessor:

1. Encodes **the cleaned `user_description` only**, with normalized embeddings.
2. Encodes all 17 entries in `SDG_DESCS` from `backend/sdg_constants.py`, also with normalized embeddings.
3. Takes the dot product of every SDG-description embedding with the user-description embedding. With normalized vectors, this is cosine similarity.
4. Uses the maximum of those 17 similarities, `max_sim`, for a single coarse decision. It does not retain or return the best-matching SDG, and does not calculate a separate recommendation per SDG.

The combined text is used for the length and keyword checks, but the embedding calculation does not use the combined text or the README/summary. This distinction matters: repository text can cause a signal-positive branch while only the submitted description is measured for similarity. An empty or very short submitted description can therefore be embedded even when the second argument contains useful text.

There is no learned relevance threshold in this recommendation scorer. Its similarity boundary is the literal, strict comparison `max_sim > 0.25`:

- `max_sim > 0.25` after signal detection: `threshold_too_high`.
- `max_sim <= 0.25` after signal detection: `signals_present_but_low_similarity`.

This `0.25` boundary is separate from the classifier routes' `0.4` prediction-output cutoff. Increasing the frontend's result confidence slider does not alter either value and does not rerun the recommendation scorer.

### `text_quality` arithmetic

The `text_quality` field is a heuristic generated by the selected branch. It is not the classifier's confidence, a calibrated probability, or a measured percentage of usable text.

| Decision branch | Formula / fixed value |
|---|---|
| Text too short | `0.3` |
| Signals found and `max_sim > 0.25` | `min(max_sim * 4, 1.0)` |
| Signals found and `max_sim <= 0.25` | `round(max_sim * 5, 2)` |
| Heavily technical | `0.4` |
| No signals | `0.2` |

Although the docstring describes a 0-to-1 score, only the `threshold_too_high` branch clamps its result. In the low-similarity branch, values just below or equal to `0.25` can produce a `text_quality` greater than `1.0` (up to `1.25` at `0.25`). Cosine similarities can also be negative, in which case multiplication can produce a negative value. The field is currently returned by the API but is not displayed in the frontend.

## 7. Decision outcomes

The following branches are evaluated in order. The first matching branch returns immediately.

### `text_too_short`

**Condition:** Fewer than 20 words across cleaned description plus second text.

**Meaning:** There is not enough combined text to continue the checks. This does not mean the project has no SDG impact.

**Suggestions returned:**
- Expand the project description to at least 20-30 words.
- Include what problem the project solves.
- Mention who benefits.

### `threshold_too_high`

**Condition:** At least 20 words, at least one keyword signal, and maximum description-to-SDG cosine similarity strictly greater than `0.25`.

**Meaning:** The code assumes the text has signals and reasonable similarity, and labels the issue a threshold problem. It does not read or inspect the classifier's actual configured threshold; this is a reason label inferred from this helper's own fixed rule.

**Suggestions returned:**
- Try increasing the SDG relevance threshold in settings.
- Provide more specific details about project impact.

### `signals_present_but_low_similarity`

**Condition:** At least 20 words, at least one keyword signal, and maximum similarity less than or equal to `0.25`.

**Meaning:** A keyword was found, but the submitted description's nearest SDG description did not pass this helper's similarity boundary.

**Suggestions returned:**
- Add specific problem statements and real-world impact.
- Include geographic or sector context, such as rural farmers or low-income countries.
- Name explicit beneficiaries, such as students, patients, or farmers.

### `heavily_technical`

**Condition:** At least 20 words, no earlier SDG/domain/problem signals, and technical-keyword count divided by word count is strictly greater than `0.5`.

**Meaning:** The helper sees technical terms without the kinds of impact signals it checks for.

**Suggestions returned:**
- Rewrite in non-technical terms, focusing on what the project does.
- Remove mentions of programming languages, frameworks, and libraries.
- Describe the real-world problem.
- Include who benefits and in what context.

### `no_sdg_signals`

**Condition:** At least 20 words, but no explicit SDG, domain, problem/beneficiary, or heavily-technical condition matched.

**Meaning:** None of the helper's listed signals appeared. It is not proof that the project is unrelated to the SDGs.

**Suggestions returned:**
- Describe the problem the project solves.
- Reduce technical jargon and focus on real-world impact.
- Identify communities, users, or beneficiaries.
- Add geographic or sector context.
- Mention the problem domain, such as health, education, or environment.

## 8. API response contract

`assess_relevance()` internally returns four keys:

```json
{
  "relevant": false,
  "reason": "no_sdg_signals",
  "text_quality": 0.2,
  "suggestions": ["..."]
}
```

The Flask routes do **not** return the `relevant` boolean. When the filtered predictions are empty, they return the other three fields under `recommendation`:

```json
{
  "projectName": "example-project",
  "projectUrl": "https://github.com/example/project",
  "predictions": [],
  "recommendation": {
    "reason": "no_sdg_signals",
    "suggestions": ["..."],
    "text_quality": 0.2
  }
}
```

When at least one prediction survives the backend cutoff, the shape is the same except `recommendation` is `null`. The frontend type in `frontend/types/main.d.ts` marks `recommendation` as optional, and the reason is represented as a string rather than a closed union of known values.

## 9. Where and how users see it

`frontend/components/results.tsx` checks the original `results.predictions` using `isNoSdgs()`:

- `null`/missing, an empty array, an empty object, or an object whose values are all missing/non-positive is treated as no SDGs.
- A non-empty array is treated as having predictions.
- Positive predictions are considered present even if a later frontend confidence slider hides them all.

When no SDGs are present, the component renders `frontend/components/noSdgPage.tsx` instead of the SDG cards. The page displays:

- A heading: “This project does not satisfy any SDG”. This is stronger wording than the helper can justify; technically the result means no prediction survived the route's filter.
- A reason message selected from the `reason` key, when a recommendation exists.
- The suggestion list returned by the backend under “Possible solutions”.
- A “Show detailed guidance” modal. Its title and textarea content use a shorter, frontend-maintained description for the selected reason; the modal does not display every returned suggestion or `text_quality`.

If no recommendation is present, the page uses generic fallback text and a fixed fallback suggestion list. In the current ordinary no-prediction cases for the two classification routes, a recommendation is included; the fallback mainly protects other response shapes or older callers.

The `text_quality` value is not currently rendered. The `relevant` key is not available to the UI because the routes omit it.

## 10. What the recommendation is and is not

It is:
- A deterministic, rule-based explanation selected from five reason categories.
- A heuristic that combines simple word-count and keyword checks with one embedding similarity comparison for signal-positive cases.
- A way to suggest improvements to the description or README summary after no predictions survived the API route's filtering.

It is not:
- A second SDG classifier or an independent validation of the classifier's predictions.
- A guarantee that the project does or does not contribute to any SDG.
- A probability, calibrated quality metric, or explanation of the classifier's internal reasoning.
- A per-SDG ranking; only the maximum similarity is used, and the matching SDG is not returned.
- A check of the classifier's actual threshold setting. The label `threshold_too_high` is a heuristic suggestion, not a measured diagnosis.
- A request for or display of more repository data. Suggestions are shown to the user; they do not modify the submitted text or automatically rerun classification.

## 11. Known implementation limitations

- **Mismatch between assessor text and embedding text:** length and keyword checks use the combined input, while similarity uses only `user_description`. README/summary context can trigger the embedding branch without contributing to its similarity value.
- **Keyword matching is broad and context-free:** substring matching can produce false positives, and missing vocabulary can produce false negatives. For example, `goal` is broad; SDG 18 is not supported as a meaningful category, but a sentence containing the word `goal` still triggers a signal.
- **The “technical ratio” is not a token frequency:** each listed technical term contributes at most one count regardless of how many times it occurs, then that count is divided by all words. It is not a conventional percentage of technical words.
- **The `threshold_too_high` message is not based on the model's actual threshold:** it is selected from `max_sim > 0.25`, independently of the route's strict `prediction > 0.4` filter.
- **The length branch comes first:** even text with obvious SDG keywords is classified as `text_too_short` if the combined word count is below 20.
- **The response drops `relevant`:** clients cannot use the intended boolean unless the route contract is changed.
- **`text_quality` is not consistently bounded:** the low-similarity formula is not clamped to `[0, 1]`.
- **Frontend wording overstates the result:** “does not satisfy any SDG” communicates a project-level conclusion, while the route only reports no scores above its filter.
- **No focused automated tests currently cover this helper or its route integration.** `backend/scripts/check_recommendation.py` is a manual smoke script with four example inputs. The general backend test guide also lists `app.py` and this kind of route behavior as lacking automated coverage.

## 12. Source map

- [backend/services/recommendation_pipeline.py](../backend/services/recommendation_pipeline.py): cleaning, word-count check, keyword categories, embedding calculation, decision branches, scores, and suggestions.
- [backend/services/embedder.py](../backend/services/embedder.py): shared lazy `all-mpnet-base-v2` model.
- [backend/sdg_constants.py](../backend/sdg_constants.py): 17 SDG descriptions used by the recommendation similarity comparison.
- [backend/app.py](../backend/app.py): recommendation invocation, `0.4` strict prediction filter, and API response assembly for both routes.
- [backend/embedding_url.py](../backend/embedding_url.py): repository text/summary source used by the ST URL path.
- [backend/services/summariser.py](../backend/services/summariser.py): Groq summary and fallback behavior used upstream of the ST URL recommendation input.
- [backend/aurora_api.py](../backend/aurora_api.py): Aurora response fields; its current output has no `project_description` field.
- [frontend/components/mainScreen.tsx](../frontend/components/mainScreen.tsx): concurrent classifier requests and Aurora fallback behavior.
- [frontend/components/results.tsx](../frontend/components/results.tsx): no-SDG detection and results-page routing.
- [frontend/components/noSdgPage.tsx](../frontend/components/noSdgPage.tsx): visible reason, suggestions, and detailed-guidance modal.
- [frontend/types/main.d.ts](../frontend/types/main.d.ts): frontend recommendation type.
- [backend/scripts/check_recommendation.py](../backend/scripts/check_recommendation.py): manual smoke examples.
