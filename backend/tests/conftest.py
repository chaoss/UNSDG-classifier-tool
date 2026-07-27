import os
import sys

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERVICES_DIR = os.path.join(BACKEND_DIR, "services")

for path in (BACKEND_DIR, SERVICES_DIR):
    if path not in sys.path:
        sys.path.insert(0, path)

# test_dpga_real_positives.py and test_gitlab_provider.py are manual,
# live-network verification scripts (see docs/TESTING.md), not pytest
# suites. Importing them during collection would pull in heavy ML deps
# (transformers, sentence-transformers) and dotenv that aren't needed to
# run the real automated tests.
collect_ignore = [
    "test_dpga_real_positives.py",
    "test_gitlab_provider.py",
]
