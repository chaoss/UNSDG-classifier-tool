import requests
import pytest

from services.api_client import APIClient
from services.errors import (
    UpstreamAPIError,
    UpstreamRateLimitError,
    UpstreamResponseError,
    UpstreamTimeoutError,
)
from services.external_apis import classify_with_aurora
from services.rate_limiter import InMemoryRateLimiter


class FakeResponse:
    def __init__(self, status_code=200, payload=None, json_error=None):
        self.status_code = status_code
        self._payload = payload
        self._json_error = json_error

    def json(self):
        if self._json_error:
            raise self._json_error
        return self._payload


class FakeSession:
    def __init__(self, outcomes):
        self.outcomes = list(outcomes)
        self.calls = []

    def request(self, method, url, **kwargs):
        self.calls.append((method, url, kwargs))
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


def make_client(outcomes, rate_limiter=None):
    return APIClient(
        timeout=1,
        max_retries=2,
        backoff_seconds=0,
        rate_limiter=rate_limiter,
        session=FakeSession(outcomes),
        sleeper=lambda seconds: None,
    )


def test_retries_retryable_status_then_returns_json():
    client = make_client([
        FakeResponse(status_code=503),
        FakeResponse(status_code=200, payload={"ok": True}),
    ])

    result = client.request_json("POST", "https://example.test", provider="aurora")

    assert result == {"ok": True}
    assert len(client.session.calls) == 2


def test_retry_backoff_uses_exponential_delays():
    delays = []
    client = APIClient(
        timeout=1,
        max_retries=2,
        backoff_seconds=0.25,
        rate_limiter=None,
        session=FakeSession([
            FakeResponse(status_code=503),
            FakeResponse(status_code=503),
            FakeResponse(status_code=503),
        ]),
        sleeper=delays.append,
    )

    with pytest.raises(UpstreamAPIError):
        client.request("POST", "https://example.test", provider="aurora")

    assert delays == [0.25, 0.5]


def test_timeout_raises_typed_exception_after_retries():
    client = make_client([
        requests.exceptions.Timeout("slow"),
        requests.exceptions.Timeout("still slow"),
        requests.exceptions.Timeout("done"),
    ])

    with pytest.raises(UpstreamTimeoutError):
        client.request("GET", "https://example.test", provider="aurora")

    assert len(client.session.calls) == 3


def test_rate_limiter_blocks_after_limit():
    now = [100.0]
    limiter = InMemoryRateLimiter(max_requests=1, window_seconds=60, clock=lambda: now[0])

    limiter.check("osdg")

    with pytest.raises(UpstreamRateLimitError):
        limiter.check("osdg")


def test_non_retryable_http_error_is_typed():
    client = make_client([FakeResponse(status_code=400)])

    with pytest.raises(UpstreamAPIError) as exc_info:
        client.request("POST", "https://example.test", provider="osdg")

    assert exc_info.value.status_code == 400


def test_invalid_json_raises_response_error():
    client = make_client([
        FakeResponse(status_code=200, json_error=ValueError("bad json")),
    ])

    with pytest.raises(UpstreamResponseError):
        client.request_json("GET", "https://example.test", provider="aurora")


def test_aurora_wrapper_rejects_invalid_predictions_shape():
    client = make_client([
        FakeResponse(status_code=200, payload={"predictions": {"bad": "shape"}}),
    ])

    with pytest.raises(UpstreamResponseError):
        classify_with_aurora("sample text", client=client)
