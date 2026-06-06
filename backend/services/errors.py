class UpstreamAPIError(Exception):
    """Base exception for external API failures."""

    def __init__(self, message, provider=None, status_code=None):
        super().__init__(message)
        self.provider = provider
        self.status_code = status_code


class UpstreamTimeoutError(UpstreamAPIError):
    """Raised when an upstream API does not respond within the timeout."""


class UpstreamRateLimitError(UpstreamAPIError):
    """Raised when local or upstream rate limits are reached."""


class UpstreamResponseError(UpstreamAPIError):
    """Raised when an upstream API returns an invalid or unexpected response."""
