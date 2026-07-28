"""
Unit tests for backend/embedding_url.py.

No real network access, no real model/embedder — `requests.post`,
`get_provider`, `get_embedder`, and `summarize_for_sdg` are all mocked, so
these run fully offline and fast. See docs/TESTING.md §2 for the coverage
checklist this file implements.
"""

from unittest.mock import MagicMock

import numpy as np
import pytest

import embedding_url
import sdg_constants
from embedding_url import ProviderError


def _mock_post_response(json_data):
    resp = MagicMock()
    resp.raise_for_status = MagicMock(return_value=None)
    resp.json = MagicMock(return_value=json_data)
    return resp


def _fake_embedder(label_scalars):
    """Encoder whose 'embeddings' are 1-D scalars, so the dot product in
    embedding_similarity_scores equals the scalar itself and pre-clip
    similarity values are fully controlled by the test."""
    def encode(texts, normalize_embeddings=True):
        if len(texts) == 1:
            return np.array([[1.0]])
        return np.array([[v] for v in label_scalars])

    embedder = MagicMock()
    embedder.encode = MagicMock(side_effect=encode)
    return embedder


def _make_zs_details(scores):
    return {
        "labels": sdg_constants.SDG_NAMES,
        "scores": list(scores),
        "sequence": "irrelevant",
    }


# ─────────────────────────── fetch_repo_text ─────────────────────────────────

class TestFetchRepoText:
    def _provider(self, owner="owner", repo="repo"):
        provider = MagicMock()
        provider._owner = owner
        provider._repo = repo
        return provider

    def test_project_description_takes_priority_over_meta_description(self, monkeypatch):
        provider = self._provider()
        provider.fetch_meta.return_value = {
            "name": "n", "description": "repo desc", "homepage": "h",
        }
        provider.fetch_topics.return_value = []
        provider.fetch_readme.return_value = ""
        monkeypatch.setattr(embedding_url, "get_provider", lambda url, token=None: provider)
        monkeypatch.setattr(embedding_url, "summarize_for_sdg", lambda **kw: "summary")

        result = embedding_url.fetch_repo_text("https://github.com/o/r", project_description="user desc")
        assert result["meta"]["description"] == "user desc"

    def test_blank_project_description_falls_back_to_meta(self, monkeypatch):
        provider = self._provider()
        provider.fetch_meta.return_value = {
            "name": "n", "description": "repo desc", "homepage": "h",
        }
        provider.fetch_topics.return_value = []
        provider.fetch_readme.return_value = ""
        monkeypatch.setattr(embedding_url, "get_provider", lambda url, token=None: provider)
        monkeypatch.setattr(embedding_url, "summarize_for_sdg", lambda **kw: "summary")

        result = embedding_url.fetch_repo_text("https://github.com/o/r", project_description="   ")
        assert result["meta"]["description"] == "repo desc"

    def test_owner_and_repo_come_from_provider_attributes(self, monkeypatch):
        provider = self._provider(owner="acme", repo="widget")
        provider.fetch_meta.return_value = {"name": "n", "description": "d", "homepage": ""}
        provider.fetch_topics.return_value = []
        provider.fetch_readme.return_value = ""
        monkeypatch.setattr(embedding_url, "get_provider", lambda url, token=None: provider)
        monkeypatch.setattr(embedding_url, "summarize_for_sdg", lambda **kw: "summary")

        result = embedding_url.fetch_repo_text("https://github.com/acme/widget")
        assert result["owner"] == "acme"
        assert result["repo"] == "widget"

    def test_none_topics_and_readme_normalized_to_empty(self, monkeypatch):
        provider = self._provider()
        provider.fetch_meta.return_value = {"name": "n", "description": "d", "homepage": ""}
        provider.fetch_topics.return_value = None
        provider.fetch_readme.return_value = None
        monkeypatch.setattr(embedding_url, "get_provider", lambda url, token=None: provider)
        captured = {}
        monkeypatch.setattr(
            embedding_url, "summarize_for_sdg",
            lambda **kw: captured.update(kw) or "summary",
        )

        result = embedding_url.fetch_repo_text("https://github.com/o/r")
        assert result["meta"]["topics"] == []
        assert captured["readme"] == ""
        assert captured["topics"] == []

    def test_summarize_called_with_name_description_topics_readme(self, monkeypatch):
        provider = self._provider()
        provider.fetch_meta.return_value = {"name": "n", "description": "d", "homepage": ""}
        provider.fetch_topics.return_value = ["a", "b"]
        provider.fetch_readme.return_value = "# readme"
        monkeypatch.setattr(embedding_url, "get_provider", lambda url, token=None: provider)
        captured = {}
        monkeypatch.setattr(
            embedding_url, "summarize_for_sdg",
            lambda **kw: captured.update(kw) or "summary",
        )

        embedding_url.fetch_repo_text("https://github.com/o/r")
        assert captured["name"] == "n"
        assert captured["description"] == "d"
        assert captured["topics"] == ["a", "b"]
        assert captured["readme"] == "# readme"

    def test_meta_error_on_first_call_recovers_on_second_call(self, monkeypatch):
        """
        fetch_repo_text wraps its first provider.fetch_meta() call in a
        try/except ProviderError, but a few lines later unconditionally
        calls provider.fetch_meta() again to build the value actually
        used in the result. That means a *transient* error on the first
        call is genuinely swallowed and doesn't abort the function -- but
        only because the second, unprotected call happens to succeed.
        """
        provider = self._provider()
        provider.fetch_meta.side_effect = [
            ProviderError("transient failure"),
            {"name": "n", "description": "d", "homepage": "h"},
        ]
        provider.fetch_topics.return_value = []
        provider.fetch_readme.return_value = ""
        monkeypatch.setattr(embedding_url, "get_provider", lambda url, token=None: provider)
        monkeypatch.setattr(embedding_url, "summarize_for_sdg", lambda **kw: "summary")

        result = embedding_url.fetch_repo_text("https://github.com/o/r")
        assert result["meta"]["name"] == "n"
        assert provider.fetch_meta.call_count == 2

    def test_persistent_meta_error_propagates(self, monkeypatch):
        """
        Pins the flip side of the above: if provider.fetch_meta() keeps
        raising ProviderError, the second (unprotected) call re-raises it
        and it propagates out of fetch_repo_text -- so "errors are caught
        and don't abort the call" only holds for transient failures, not
        persistent ones.
        """
        provider = self._provider()
        provider.fetch_meta.side_effect = ProviderError("persistent failure")
        provider.fetch_topics.return_value = []
        provider.fetch_readme.return_value = ""
        monkeypatch.setattr(embedding_url, "get_provider", lambda url, token=None: provider)
        monkeypatch.setattr(embedding_url, "summarize_for_sdg", lambda **kw: "summary")

        with pytest.raises(ProviderError):
            embedding_url.fetch_repo_text("https://github.com/o/r")

    def test_topics_error_on_first_call_recovers_on_second_call(self, monkeypatch):
        provider = self._provider()
        provider.fetch_meta.return_value = {"name": "n", "description": "d", "homepage": ""}
        provider.fetch_topics.side_effect = [ProviderError("transient"), ["x", "y"]]
        provider.fetch_readme.return_value = ""
        monkeypatch.setattr(embedding_url, "get_provider", lambda url, token=None: provider)
        monkeypatch.setattr(embedding_url, "summarize_for_sdg", lambda **kw: "summary")

        result = embedding_url.fetch_repo_text("https://github.com/o/r")
        assert result["meta"]["topics"] == ["x", "y"]

    def test_readme_error_on_first_call_recovers_on_second_call(self, monkeypatch):
        provider = self._provider()
        provider.fetch_meta.return_value = {"name": "n", "description": "d", "homepage": ""}
        provider.fetch_topics.return_value = []
        provider.fetch_readme.side_effect = [ProviderError("transient"), "recovered readme"]
        monkeypatch.setattr(embedding_url, "get_provider", lambda url, token=None: provider)
        captured = {}
        monkeypatch.setattr(
            embedding_url, "summarize_for_sdg",
            lambda **kw: captured.update(kw) or "summary",
        )

        embedding_url.fetch_repo_text("https://github.com/o/r")
        assert captured["readme"] == "recovered readme"


# ─────────────────────────── zero_shot_scores ────────────────────────────────

class TestZeroShotScores:
    def test_score_ordering_matches_sdg_names(self, monkeypatch):
        # Reverse-order mapping so the assertion can't pass by accident of
        # dict/list ordering matching SDG_NAMES ordering already.
        scrambled = dict(zip(reversed(sdg_constants.SDG_NAMES), range(17)))
        monkeypatch.setattr(
            embedding_url.requests, "post",
            MagicMock(return_value=_mock_post_response({"scores": scrambled})),
        )

        arr, _ = embedding_url.zero_shot_scores("text", sdg_constants.SDG_NAMES)

        expected = [16 - i for i in range(17)]
        np.testing.assert_array_equal(arr, expected)

    def test_missing_expected_key_raises_key_error(self, monkeypatch):
        incomplete = {name: 0.5 for name in sdg_constants.SDG_NAMES[:-1]}
        monkeypatch.setattr(
            embedding_url.requests, "post",
            MagicMock(return_value=_mock_post_response({"scores": incomplete})),
        )

        with pytest.raises(KeyError):
            embedding_url.zero_shot_scores("text", sdg_constants.SDG_NAMES)

    def test_unexpected_scores_type_raises_type_error(self, monkeypatch):
        monkeypatch.setattr(
            embedding_url.requests, "post",
            MagicMock(return_value=_mock_post_response({"scores": 42})),
        )

        with pytest.raises(TypeError):
            embedding_url.zero_shot_scores("text", sdg_constants.SDG_NAMES)

    def test_nested_data_scores_shape_handled(self, monkeypatch):
        full = {name: 0.5 for name in sdg_constants.SDG_NAMES}
        monkeypatch.setattr(
            embedding_url.requests, "post",
            MagicMock(return_value=_mock_post_response({"data": {"scores": full}})),
        )

        arr, _ = embedding_url.zero_shot_scores("text", sdg_constants.SDG_NAMES)
        assert arr.shape == (17,)
        assert (arr == 0.5).all()

    def test_list_scores_type_hits_unbound_local_error(self, monkeypatch):
        """
        Pins a real bug: in the `elif isinstance(scores_obj, (list, tuple))`
        branch, the code assigns `scores_list` but the function's final
        `return` statement reads `ordered_scores`, which is only ever
        assigned in the dict branch above it. A list/tuple `scores` payload
        therefore raises UnboundLocalError instead of returning scores.
        """
        monkeypatch.setattr(
            embedding_url.requests, "post",
            MagicMock(return_value=_mock_post_response({"scores": list(range(17))})),
        )

        with pytest.raises(UnboundLocalError):
            embedding_url.zero_shot_scores("text", sdg_constants.SDG_NAMES)

    def test_detailed_info_sequence_truncated_to_500_chars(self, monkeypatch):
        full = {name: 0.1 for name in sdg_constants.SDG_NAMES}
        monkeypatch.setattr(
            embedding_url.requests, "post",
            MagicMock(return_value=_mock_post_response({"scores": full})),
        )

        _, details = embedding_url.zero_shot_scores("x" * 600, sdg_constants.SDG_NAMES)
        assert len(details["sequence"]) == 500
        assert details["labels"] == sdg_constants.SDG_NAMES


# ─────────────────────────── embedding_similarity_scores ─────────────────────

class TestEmbeddingSimilarityScores:
    def test_output_clipped_and_scaled_to_unit_range(self, monkeypatch):
        # COSINE_LOW=0.27, COSINE_HIGH=0.34
        label_scalars = [0.20, 0.27, 0.305, 0.34, 0.50]
        monkeypatch.setattr(embedding_url, "get_embedder", lambda: _fake_embedder(label_scalars))

        sims = embedding_url.embedding_similarity_scores(
            "some text", ["l1", "l2", "l3", "l4", "l5"]
        )

        np.testing.assert_allclose(sims, [0.0, 0.0, 0.5, 1.0, 1.0], atol=1e-9)


# ─────────────────────────── ensemble_scores ──────────────────────────────────

class TestEnsembleScores:
    def test_alpha_zero_returns_embedding_scores(self):
        zs = np.array([0.1, 0.9])
        es = np.array([0.4, 0.6])
        result = embedding_url.ensemble_scores(zs, es, alpha=0.0)
        np.testing.assert_allclose(result, es)

    def test_alpha_one_returns_zero_shot_scores(self):
        zs = np.array([0.1, 0.9])
        es = np.array([0.4, 0.6])
        result = embedding_url.ensemble_scores(zs, es, alpha=1.0)
        np.testing.assert_allclose(result, zs)

    def test_default_alpha_is_weighted_average(self):
        zs = np.array([1.0, 0.0])
        es = np.array([0.0, 1.0])
        result = embedding_url.ensemble_scores(zs, es)  # alpha defaults to 0.3
        np.testing.assert_allclose(result, [0.3, 0.7])


# ─────────────────────────── classify_repo ────────────────────────────────────

class TestClassifyRepo:
    def _patch_fetch(self, monkeypatch, text="some extracted text", owner="owner", repo="repo"):
        monkeypatch.setattr(
            embedding_url, "fetch_repo_text",
            lambda url, project_description="": {
                "owner": owner,
                "repo": repo,
                "text": text,
                "meta": {"name": "n", "description": "d", "topics": [], "homepage": ""},
            },
        )

    def test_empty_extracted_text_raises_value_error(self, monkeypatch):
        self._patch_fetch(monkeypatch, text="")
        with pytest.raises(ValueError):
            embedding_url.classify_repo("https://github.com/o/r")

    def test_predictions_above_threshold_selected(self, monkeypatch):
        self._patch_fetch(monkeypatch)
        zs = np.zeros(17)
        zs[0] = 0.9
        zs[2] = 0.8
        monkeypatch.setattr(embedding_url, "zero_shot_scores", lambda text, labels: (zs, _make_zs_details(zs)))
        monkeypatch.setattr(embedding_url, "embedding_similarity_scores", lambda text, label_texts: zs)

        result = embedding_url.classify_repo("https://github.com/o/r", threshold=0.5, use_ensemble=True)

        selected_names = [name for name, _ in result["predictions"]]
        assert set(selected_names) == {sdg_constants.SDG_NAMES[0], sdg_constants.SDG_NAMES[2]}

    def test_falls_back_to_top_three_when_nothing_clears_threshold(self, monkeypatch):
        self._patch_fetch(monkeypatch)
        zs = np.full(17, 0.1)
        zs[5], zs[1], zs[9] = 0.3, 0.25, 0.2
        monkeypatch.setattr(embedding_url, "zero_shot_scores", lambda text, labels: (zs, _make_zs_details(zs)))
        monkeypatch.setattr(embedding_url, "embedding_similarity_scores", lambda text, label_texts: zs)

        result = embedding_url.classify_repo("https://github.com/o/r", threshold=0.99, use_ensemble=True)

        assert len(result["predictions"]) == 3
        assert result["predictions"] == result["top_all"][:3]

    def test_use_ensemble_false_skips_embedding_similarity_call(self, monkeypatch):
        self._patch_fetch(monkeypatch)
        zs = np.zeros(17)
        zs[0] = 0.9
        monkeypatch.setattr(embedding_url, "zero_shot_scores", lambda text, labels: (zs, _make_zs_details(zs)))
        embedding_sim_mock = MagicMock()
        monkeypatch.setattr(embedding_url, "embedding_similarity_scores", embedding_sim_mock)

        result = embedding_url.classify_repo("https://github.com/o/r", threshold=0.5, use_ensemble=False)

        embedding_sim_mock.assert_not_called()
        assert sdg_constants.SDG_NAMES[0] in [n for n, _ in result["predictions"]]

    def test_repo_and_meta_come_from_fetch_repo_text(self, monkeypatch):
        self._patch_fetch(monkeypatch, owner="acme", repo="widget")
        zs = np.zeros(17)
        zs[0] = 0.9
        monkeypatch.setattr(embedding_url, "zero_shot_scores", lambda text, labels: (zs, _make_zs_details(zs)))
        monkeypatch.setattr(embedding_url, "embedding_similarity_scores", lambda text, label_texts: zs)

        result = embedding_url.classify_repo("https://github.com/acme/widget", threshold=0.5)

        assert result["repo"] == "acme/widget"
        assert result["meta"] == {"name": "n", "description": "d", "topics": [], "homepage": ""}


# ─────────────────────────── main ──────────────────────────────────────────────

class TestMain:
    def test_scores_formatted_to_three_decimals(self, monkeypatch):
        monkeypatch.setattr(
            embedding_url, "classify_repo",
            lambda url, threshold, use_ensemble, proj_desc: {
                "repo": "owner/repo",
                "predictions": [
                    ("SDG 1: End poverty in all its forms everywhere", 0.123456),
                    ("SDG 3: Ensure healthy lives and promote well-being for all at all ages", 0.98765),
                ],
            },
        )

        result = embedding_url.main("https://github.com/owner/repo")

        assert result["project_name"] == "owner/repo"
        assert result["project_url"] == "https://github.com/owner/repo"
        assert result["sdg_predictions"] == {
            "SDG 1: End poverty in all its forms everywhere": 0.123,
            "SDG 3: Ensure healthy lives and promote well-being for all at all ages": 0.988,
        }
