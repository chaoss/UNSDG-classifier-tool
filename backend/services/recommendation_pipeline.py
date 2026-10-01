"""
recommendation_pipeline.py


A pipeline that determines why a project may not have received any SDG
classifications and provides recommendations for improving the input data.

Uses the existing sentence-transformers embedder (no LLM required) to
assess text relevance against SDG descriptions.

Returns a structured result containing:
- reason: brief explanation of why no SDGs were found
- suggestions: list of actionable improvements
- text_quality: score 0-1 indicating how much usable content exists
"""

import re
from functools import lru_cache
from typing import Tuple

import numpy as np

from sdg_constants import SDG_DESCS, SDG_NAMES
from services.embedder import get_embedder



def _clean_text(raw: str) -> str:
    """Basic cleaning: strip, collapse whitespace, remove bare URLs."""
    text = raw.strip()
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"https?://\S+", "", text)
    return text


def _is_too_short(text: str, min_words: int = 15) -> bool:
    """Check if text has fewer than min_words after cleaning."""
    cleaned = _clean_text(text)
    return len(cleaned.split()) < min_words


def _contains_keyword(text: str, keyword: str) -> bool:
    pattern = r"\b" + r"\s+".join(re.escape(part) for part in keyword.split()) + r"\b"
    return re.search(pattern, text) is not None


def _combine_text(description: str, readme: str) -> str:
    
    normalized_description = " ".join(description.casefold().split())
    normalized_readme = " ".join(readme.casefold().split())
    if normalized_description and normalized_description in normalized_readme:
        return readme
    return f"{description} {readme}"


@lru_cache(maxsize=1)
def _get_sdg_embeddings() -> np.ndarray:
    """Encode the SDG descriptions once, on the first embedding-based assessment."""
    embeddings = get_embedder().encode(
        SDG_DESCS,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )
    return np.asarray(embeddings)


def _encode_text_chunks(text: str, embedder) -> np.ndarray:
    tokenizer = embedder.tokenizer
    max_content_tokens = embedder.max_seq_length - tokenizer.num_special_tokens_to_add(pair=False)
    token_ids = tokenizer.encode(text, add_special_tokens=False)
    if not token_ids:
        chunks = [text]
    else:
        token_chunks = [
            token_ids[index:index + max_content_tokens]
            for index in range(0, len(token_ids), max_content_tokens)
        ]
        chunks = tokenizer.batch_decode(
            token_chunks,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=True,
        )
    return np.asarray(embedder.encode(
        chunks,
        normalize_embeddings=True,
        convert_to_numpy=True,
    ))


def _bounded_quality(value: float) -> float:
    if not np.isfinite(value):
        return 0.0
    return float(np.clip(value, 0.0, 1.0))


def _has_sdg_signals(text: str) -> Tuple[bool, str]:
    """
    Check if text contains signals that could map to SDGs.
    Returns (has_signals, reason_category).
    
    Checks for:
    - Explicit SDG number/name mentions
    - Domain-specific vocabulary (health, education, environment, etc.)
    - Problem/beneficiary descriptions
    """
    cleaned = _clean_text(text).lower()

    # Explicit SDG mentions
    sdg_keywords = ["sdg", "sustainable development", "goal"]
    for kw in sdg_keywords:
        if _contains_keyword(cleaned, kw):
            return True, "sdg_mentioned"

    # Domain-specific vocabulary that maps to SDG topics
    domain_keywords = {
        "health": ["health", "medical", "hospital", "patient", "clinical"],
        "education": ["education", "learning", "school", "student", "teaching"],
        "environment": ["environment", "climate", "ecological", "sustainability"],
        "water": ["water", "sanitation", "hygiene", "wash"],
        "energy": ["energy", "power", "electricity", "renewable"],
        "agriculture": ["agriculture", "farm", "farming", "crop", "rural"],
        "governance": ["governance", "policy", "government"],
        "gender": ["gender", "women", "equality", "female"],
    }

    found_categories = []
    for category, keywords in domain_keywords.items():
        if any(_contains_keyword(cleaned, kw) for kw in keywords):
            found_categories.append(category)

    if found_categories:
        return True, "domain_signals"

    # Check for problem/beneficiary language
    problem_keywords = ["problem", "solution", "beneficiaries", "users", "impact",
                        "helps", "addresses", "reduces", "improves"]
    if any(_contains_keyword(cleaned, kw) for kw in problem_keywords):
        return True, "problem_description"

    # Check for heavily technical content (e.g., code, libraries, frameworks)
    tech_keywords = ["python", "javascript", "react", "api", "database",
                     "framework", "library", "container", "docker", "cls",
                     "function", "import", "class", "module"]
    tech_count = sum(1 for kw in tech_keywords if _contains_keyword(cleaned, kw))
    
    # If >40% of keywords are technical, flag as heavily technical
    word_count = len(cleaned.split())
    if word_count > 0 and tech_count / word_count > 0.4:
        return False, "heavily_technical"
    
    return False, "no_signals"


def assess_relevance(
    user_description: str,
    readme_text: str,
) -> dict:
    """
    Assess whether the provided text is relevant enough for SDG classification.
    
    Uses embedding similarity against SDG descriptions to determine if
    the text has sufficient content to classify, without using an LLM.
    
    Returns:
        dict with keys:
        - relevant: bool - whether text is sufficiently relevant
        - reason: str - category of issue if not relevant
        - text_quality: float 0-1 - how much usable content exists
        - suggestions: List[str] - actionable recommendations
    """
    # Clean both inputs
    desc_clean = _clean_text(user_description)
    readme_clean = _clean_text(readme_text)
    
    # Check combined text first
    combined = _combine_text(desc_clean, readme_clean)
    
    # Step 1: Check if too short
    if _is_too_short(combined, min_words=20):
        return {
            "relevant": False,
            "reason": "text_too_short",
            "text_quality": 0.3,
            "suggestions": [
                "Expand your project description to at least 20-30 words",
                "Include what problem your project solves",
                "Mention who benefits from your project",
            ],
        }
    
    # Step 2: Check for SDG signals
    has_signals, signal_reason = _has_sdg_signals(combined)
    
    if has_signals:
        embedder = get_embedder()
        description_embeddings = _encode_text_chunks(desc_clean, embedder)
        sdg_embs = _get_sdg_embeddings()
        sims_by_chunk = np.dot(description_embeddings, sdg_embs.T)
        sims = np.max(sims_by_chunk, axis=0)
        max_index = int(np.argmax(sims))
        max_sim = float(sims[max_index])
        nearest_sdg = SDG_NAMES[max_index]
        
        if max_sim > 0.25:
            # Has signals and good similarity - just threshold issue
            return {
                "relevant": True,
                "reason": "threshold_too_high",
                "text_quality": _bounded_quality(max_sim * 4),
                "suggestions": [
                    "Provide more specific details about your project's impact",
                    "Name the communities or beneficiaries your project supports",
                ],
                "nearest_sdg": nearest_sdg,
                "nearest_similarity": max_sim,
            }
        
        # Has signals but low similarity - might need more detail
        return {
            "relevant": True,
            "reason": "signals_present_but_low_similarity",
            "text_quality": _bounded_quality(max_sim * 5),
            "suggestions": [
                "Add more specific problem statements and real-world impact",
                "Include geographic or sector context (e.g., 'rural farmers', 'low-income countries')",
                "Mention explicit beneficiaries (e.g., 'students', 'patients', 'farmers')",
            ],
            "nearest_sdg": nearest_sdg,
            "nearest_similarity": max_sim,
        }
    # Step 3: No signals detected - check if heavily technical
    if signal_reason == "heavily_technical":
        return {
            "relevant": False,
            "reason": "heavily_technical",
            "text_quality": 0.4,
            "suggestions": [
                "Rewrite description in non-technical terms - focus on what the project does, not how",
                "Remove mentions of programming languages, frameworks, and libraries",
                "Describe the real-world problem your project addresses",
                "Include who benefits and in what context",
            ],
        }
    
    # Step 4: No signals at all
    return {
        "relevant": False,
        "reason": "no_sdg_signals",
        "text_quality": 0.2,
        "suggestions": [
            "Make description more elaborate - describe the problem your project solves",
            "Reduce technical jargon and focus on real-world impact",
            "Include who benefits from your project (communities, users, beneficiaries)",
            "Add geographic or sector context (e.g., 'rural areas', 'low-income countries')",
            "Mention the specific problem type (health, education, environment, etc.)",
        ],
    }