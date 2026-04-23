from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from crawler.config import load_config


class ConfigLoaderTests(unittest.TestCase):
    def test_load_config_returns_typed_sources(self) -> None:
        payload = {
            "version": "test",
            "user_agent": "ua",
            "sources": [
                {
                    "id": "demo",
                    "label": "Demo",
                    "weight": 1,
                    "region": "CN",
                    "transport": "direct",
                    "observed_on": "2026-04-23",
                    "observed_status": "ok",
                    "home_url": "https://example.com/",
                }
            ],
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "config.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            config = load_config(path)
        self.assertEqual(config.version, "test")
        self.assertEqual(config.sources[0].id, "demo")

    def test_manual_curated_override_is_merged(self) -> None:
        payload = {
            "version": "test",
            "user_agent": "ua",
            "sources": [
                {
                    "id": "demo",
                    "label": "Demo",
                    "weight": 1,
                    "region": "CN",
                    "transport": "direct",
                    "observed_on": "2026-04-23",
                    "observed_status": "ok",
                    "home_url": "https://example.com/",
                    "curated_urls": ["https://example.com/a"]
                }
            ],
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "config.json"
            override = Path(tmpdir) / 'manual_curated_urls.json'
            path.write_text(json.dumps(payload), encoding="utf-8")
            override.write_text(json.dumps({"demo": ["https://example.com/b"]}), encoding='utf-8')
            with patch('crawler.config.MANUAL_CURATED_OVERRIDES', override):
                config = load_config(path)
        self.assertEqual(config.sources[0].curated_urls, ('https://example.com/a', 'https://example.com/b'))


if __name__ == "__main__":
    unittest.main()
