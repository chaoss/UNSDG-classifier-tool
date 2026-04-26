"""Centralized runtime configuration for the UN-SDG classifier backend.

External service endpoints and credentials are read from environment variables
so deployments can be reconfigured without code changes. Defaults match the
historical hardcoded values so existing local setups keep working.

See ``backend/.env.example`` for the full list of supported variables.
"""

import os
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parent
ENV_FILE = BACKEND_DIR / ".env"

try:
    from dotenv import load_dotenv

    # Load a .env file from the backend/ directory if one exists.
    # Safe to call when the file is absent.
    load_dotenv(ENV_FILE)
except ImportError:
    # python-dotenv is optional; environment variables set by the host
    # process are still honored.
    pass


def _get(name: str, default: str = "") -> str:
    value = os.environ.get(name)
    return value.strip() if value and value.strip() else default


def _get_positive_int(name: str, default: int) -> int:
    raw_value = _get(name, str(default))
    try:
        value = int(raw_value)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer number of seconds") from exc

    if value <= 0:
        raise ValueError(f"{name} must be greater than 0")

    return value


# --- External classifier endpoints ----------------------------------------

AURORA_API_URL: str = _get(
    "AURORA_API_URL",
    "https://aurora-sdg.labs.vu.nl/classifier/classify/elsevier-sdg-multi",
)

OSDG_API_URL: str = _get(
    "OSDG_API_URL",
    "http://20.73.166.85/label_text",
)

GITHUB_API_URL: str = _get(
    "GITHUB_API_URL",
    "https://api.github.com",
).rstrip("/")


# --- Credentials ----------------------------------------------------------

# Optional. Required only when using the OSDG endpoint.
OSDG_TOKEN: str = _get("OSDG_TOKEN")

# Optional. When set, GitHub API requests are authenticated, raising the
# rate limit from 60 to 5000 requests/hour.
GITHUB_TOKEN: str = _get("GITHUB_TOKEN")


# --- Request tuning -------------------------------------------------------

# Timeout (seconds) for outbound HTTP requests to external services.
HTTP_TIMEOUT_SECONDS: int = _get_positive_int("HTTP_TIMEOUT_SECONDS", 30)
