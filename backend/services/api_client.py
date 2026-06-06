import time

import requests

from services.errors import (
    UpstreamAPIError,
    UpstreamRateLimitError,
    UpstreamResponseError,
    UpstreamTimeoutError,
)
from services.rate_limiter import DEFAULT_RATE_LIMITER


RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


class APIClient:
    """Small requests-based client with timeouts, retries, and local limiting."""

    def __init__(
        self,
        timeout=10,
        max_retries=2,
        backoff_seconds=0.25,
        rate_limiter=DEFAULT_RATE_LIMITER,
        session=None,
        sleeper=None,
    ):
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_seconds = backoff_seconds
        self.rate_limiter = rate_limiter
        self.session = session or requests.Session()
        self._sleep = sleeper or time.sleep

    def request(self, method, url, provider, **kwargs):
        if self.rate_limiter:
            self.rate_limiter.check(provider)

        request_timeout = kwargs.pop("timeout", self.timeout)
        last_error = None

        for attempt in range(self.max_retries + 1):
            try:
                response = self.session.request(
                    method,
                    url,
                    timeout=request_timeout,
                    **kwargs,
                )
            except requests.exceptions.Timeout as exc:
                last_error = UpstreamTimeoutError(
                    f"{provider} request timed out",
                    provider=provider,
                )
            except requests.exceptions.RequestException as exc:
                last_error = UpstreamAPIError(
                    f"{provider} request failed: {exc}",
                    provider=provider,
                )
            else:
                if response.status_code == 429:
                    last_error = UpstreamRateLimitError(
                        f"{provider} rate limit exceeded",
                        provider=provider,
                        status_code=response.status_code,
                    )
                elif response.status_code in RETRYABLE_STATUS_CODES:
                    last_error = UpstreamAPIError(
                        f"{provider} returned status {response.status_code}",
                        provider=provider,
                        status_code=response.status_code,
                    )
                elif response.status_code >= 400:
                    raise UpstreamAPIError(
                        f"{provider} returned status {response.status_code}",
                        provider=provider,
                        status_code=response.status_code,
                    )
                else:
                    return response

            if attempt < self.max_retries:
                self._sleep(self.backoff_seconds * (2**attempt))

        raise last_error

    def request_json(self, method, url, provider, **kwargs):
        response = self.request(method, url, provider, **kwargs)
        try:
            return response.json()
        except ValueError as exc:
            raise UpstreamResponseError(
                f"{provider} returned invalid JSON",
                provider=provider,
                status_code=response.status_code,
            ) from exc
