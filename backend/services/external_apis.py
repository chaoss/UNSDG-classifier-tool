import os

from services.api_client import APIClient
from services.errors import UpstreamResponseError


AURORA_CLASSIFY_URL = (
    "https://aurora-sdg.labs.vu.nl/classifier/classify/elsevier-sdg-multi"
)
# Prefer an HTTPS OSDG endpoint when one is available; keep the current URL as
# the fallback to preserve existing local behavior.
OSDG_LABEL_URL = os.environ.get("OSDG_LABEL_URL", "http://20.73.166.85/label_text")

_client = APIClient()


def classify_with_aurora(text, client=None):
    api_client = client or _client
    result = api_client.request_json(
        "POST",
        AURORA_CLASSIFY_URL,
        provider="aurora",
        json={"text": text},
        headers={"Content-Type": "application/json"},
    )

    if not isinstance(result, dict):
        raise UpstreamResponseError(
            "Aurora returned an unexpected response",
            provider="aurora",
        )

    predictions = result.get("predictions")
    if predictions is not None and not isinstance(predictions, list):
        raise UpstreamResponseError(
            "Aurora predictions must be a list",
            provider="aurora",
        )

    return result


def classify_with_osdg(text, client=None):
    api_client = client or _client
    result = api_client.request_json(
        "POST",
        OSDG_LABEL_URL,
        provider="osdg",
        json={"text": text},
        headers={"token": os.environ.get("OSDG_TOKEN", "")},
    )

    if not isinstance(result, (dict, list)):
        raise UpstreamResponseError(
            "OSDG returned an unexpected response",
            provider="osdg",
        )

    return result
