import importlib
import os
import sys
import unittest
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
CONFIG_ENV_VARS = {
    "AURORA_API_URL",
    "OSDG_API_URL",
    "GITHUB_API_URL",
    "OSDG_TOKEN",
    "GITHUB_TOKEN",
    "HTTP_TIMEOUT_SECONDS",
}

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


class ConfigTestCase(unittest.TestCase):
    def load_config(self, env=None):
        env = env or {}
        previous_values = {name: os.environ.get(name) for name in CONFIG_ENV_VARS}

        try:
            for name in CONFIG_ENV_VARS:
                os.environ.pop(name, None)
            os.environ.update(env)

            sys.modules.pop("config", None)
            return importlib.import_module("config")
        finally:
            for name in CONFIG_ENV_VARS:
                os.environ.pop(name, None)
            for name, value in previous_values.items():
                if value is not None:
                    os.environ[name] = value

    def test_defaults_match_existing_service_values(self):
        config = self.load_config()

        self.assertEqual(
            config.AURORA_API_URL,
            "https://aurora-sdg.labs.vu.nl/classifier/classify/elsevier-sdg-multi",
        )
        self.assertEqual(config.OSDG_API_URL, "http://20.73.166.85/label_text")
        self.assertEqual(config.GITHUB_API_URL, "https://api.github.com")
        self.assertEqual(config.OSDG_TOKEN, "")
        self.assertEqual(config.GITHUB_TOKEN, "")
        self.assertEqual(config.HTTP_TIMEOUT_SECONDS, 30)

    def test_environment_values_override_defaults(self):
        config = self.load_config(
            {
                "AURORA_API_URL": "https://example.test/aurora",
                "OSDG_API_URL": "https://example.test/osdg",
                "GITHUB_API_URL": "https://github.example.test/api/v3/",
                "OSDG_TOKEN": "osdg-token",
                "GITHUB_TOKEN": "github-token",
                "HTTP_TIMEOUT_SECONDS": "12",
            }
        )

        self.assertEqual(config.AURORA_API_URL, "https://example.test/aurora")
        self.assertEqual(config.OSDG_API_URL, "https://example.test/osdg")
        self.assertEqual(config.GITHUB_API_URL, "https://github.example.test/api/v3")
        self.assertEqual(config.OSDG_TOKEN, "osdg-token")
        self.assertEqual(config.GITHUB_TOKEN, "github-token")
        self.assertEqual(config.HTTP_TIMEOUT_SECONDS, 12)

    def test_blank_environment_values_fall_back_to_defaults(self):
        config = self.load_config(
            {
                "AURORA_API_URL": "   ",
                "OSDG_API_URL": "",
                "GITHUB_API_URL": " ",
                "HTTP_TIMEOUT_SECONDS": "",
            }
        )

        self.assertEqual(
            config.AURORA_API_URL,
            "https://aurora-sdg.labs.vu.nl/classifier/classify/elsevier-sdg-multi",
        )
        self.assertEqual(config.OSDG_API_URL, "http://20.73.166.85/label_text")
        self.assertEqual(config.GITHUB_API_URL, "https://api.github.com")
        self.assertEqual(config.HTTP_TIMEOUT_SECONDS, 30)

    def test_timeout_must_be_positive_integer(self):
        with self.assertRaisesRegex(ValueError, "HTTP_TIMEOUT_SECONDS"):
            self.load_config({"HTTP_TIMEOUT_SECONDS": "not-a-number"})

        with self.assertRaisesRegex(ValueError, "HTTP_TIMEOUT_SECONDS"):
            self.load_config({"HTTP_TIMEOUT_SECONDS": "0"})


if __name__ == "__main__":
    unittest.main()
