from unittest.mock import MagicMock

import numpy as np
import pytest

import app as flask_app
import sdg_constants
from app import SDG_PREDICTION_CUTOFF, _filter_predictions
from services import recommendation_pipeline as pipeline


class _WhitespaceTokenizer:
    def encode(self, text, add_special_tokens=False):
        return text.split()

    def num_special_tokens_to_add(self, pair=False):
        return 2

    def batch_decode(self, token_chunks, **_kwargs):
        return [" ".join(chunk) for chunk in token_chunks]


@pytest.fixture(autouse=True)
def clear_embedding_cache():
    pipeline._get_sdg_embeddings.cache_clear()
    yield
    pipeline._get_sdg_embeddings.cache_clear()


def _mock_embedder(monkeypatch, similarities):
    embedder = MagicMock()
    embedder.tokenizer = _WhitespaceTokenizer()
    embedder.max_seq_length = 14

    def encode(texts, **_kwargs):
        if len(texts) == len(sdg_constants.SDG_DESCS):
            return similarities
        return np.tile(np.array([[1.0, 0.0]]), (len(texts), 1))

    embedder.encode.side_effect = encode
    monkeypatch.setattr(pipeline, "get_embedder", lambda: embedder)
    return embedder


def _impact_description():
    return (
        "Our education program supports students with accessible lessons and "
        "community mentors, improving learning outcomes for rural families and "
        "young people across underserved regions through affordable local services."
    )


def test_route_cutoff_is_shared_and_strict():
    assert SDG_PREDICTION_CUTOFF == 0.4
    assert _filter_predictions([
        {"sdg": "SDG 1", "prediction": 0.3},
        {"sdg": "SDG 2", "prediction": 0.4},
        {"sdg": "SDG 3", "prediction": 0.4001},
    ]) == [{"sdg": "SDG 3", "prediction": 0.4001}]


@pytest.mark.parametrize(
    "text",
    [
        "The goalkeeper compares several healthcare products for a local club.",
        "A goalkeeper keeps records for a community football team.",
        "Reactive components render cards in a small frontend application.",
    ],
)
def test_keywords_do_not_match_inside_other_words(text):
    assert pipeline._has_sdg_signals(text) == (False, "no_signals")


def test_keyword_matches_complete_words_and_multiword_phrases():
    assert pipeline._has_sdg_signals("Progress toward sustainable\n development matters.") == (
        True,
        "sdg_mentioned",
    )


def test_description_already_in_summary_is_counted_once():
    description = "A short description with only twelve total words for this test case."
    combined = pipeline._combine_text(description, f"Project name. {description}.")

    assert combined == f"Project name. {description}."
    assert pipeline._is_too_short(combined, min_words=20)


def test_sdg_embeddings_are_reused_and_nearest_sdg_is_returned(monkeypatch):
    similarities = np.zeros((len(sdg_constants.SDG_DESCS), 2))
    similarities[3] = [0.5, 0.0]
    embedder = _mock_embedder(monkeypatch, similarities)
    description = _impact_description()

    first = pipeline.assess_relevance(description, description)
    second = pipeline.assess_relevance(description, description)

    assert first["reason"] == second["reason"] == "threshold_too_high"
    assert first["nearest_sdg"] == sdg_constants.SDG_NAMES[3]
    assert first["nearest_similarity"] == pytest.approx(0.5)
    assert first["text_quality"] == 1.0
    assert all("threshold" not in suggestion.lower() for suggestion in first["suggestions"])
    query_calls = [
        call for call in embedder.encode.call_args_list
        if len(call.args[0]) != len(sdg_constants.SDG_DESCS)
    ]
    assert len(query_calls[0].args[0]) == 3
    assert sum(len(call.args[0]) == len(sdg_constants.SDG_DESCS) for call in embedder.encode.call_args_list) == 1


def test_low_similarity_quality_is_clamped_to_unit_interval(monkeypatch):
    similarities = np.full((len(sdg_constants.SDG_DESCS), 2), -0.2)
    _mock_embedder(monkeypatch, similarities)

    result = pipeline.assess_relevance(_impact_description(), "")

    assert result["reason"] == "signals_present_but_low_similarity"
    assert result["text_quality"] == 0.0
    assert 0.0 <= result["text_quality"] <= 1.0


def test_st_route_returns_separate_readme_assessment(monkeypatch):
    seen = []
    monkeypatch.setattr(
        flask_app,
        "classify_url",
        lambda **_kwargs: {
            "summary": "classifier summary",
            "readme_excerpt": "cleaned README excerpt",
            "meta": {"description": "repository description"},
            "sdg_predictions": {},
        },
    )

    def assess(description, readme):
        seen.append((description, readme))
        return {
            "relevant": description == "cleaned README excerpt",
            "reason": "no_sdg_signals",
            "text_quality": 0.2,
            "suggestions": [],
        }

    monkeypatch.setattr(flask_app, "assess_relevance", assess)
    response = flask_app.app.test_client().post(
        "/api/classify_st_url",
        json={
            "projectName": "project",
            "projectUrl": "https://github.com/example/project",
            "projectDescription": "user description",
        },
    )

    assert response.status_code == 200
    assert seen == [
        ("user description", "classifier summary"),
        ("cleaned README excerpt", ""),
    ]
    assert response.get_json()["readme_assessment"]["relevant"] is True