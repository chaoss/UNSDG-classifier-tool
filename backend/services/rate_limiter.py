import threading
import time
from collections import deque

from services.errors import UpstreamRateLimitError


class InMemoryRateLimiter:
    """Thread-safe sliding-window limiter for low-volume Flask deployments."""

    def __init__(self, max_requests, window_seconds, clock=None):
        if max_requests <= 0:
            raise ValueError("max_requests must be greater than zero")
        if window_seconds <= 0:
            raise ValueError("window_seconds must be greater than zero")

        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._clock = clock or time.monotonic
        self._requests = {}
        self._lock = threading.Lock()

    def check(self, key):
        now = self._clock()
        cutoff = now - self.window_seconds

        with self._lock:
            timestamps = self._requests.setdefault(key, deque())
            while timestamps and timestamps[0] <= cutoff:
                timestamps.popleft()

            if len(timestamps) >= self.max_requests:
                raise UpstreamRateLimitError(
                    "Rate limit exceeded. Please try again later.",
                    provider=key,
                    status_code=429,
                )

            timestamps.append(now)


DEFAULT_RATE_LIMITER = InMemoryRateLimiter(max_requests=30, window_seconds=60)
