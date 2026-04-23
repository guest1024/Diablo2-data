from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from crawler.validate_manual_curated_urls import main


class ValidateManualCuratedUrlsTests(unittest.TestCase):
    def test_missing_manual_file_is_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config = Path(tmpdir) / 'config.json'
            config.write_text(json.dumps({
                'version': 'test',
                'sources': [{
                    'id': 'demo',
                    'label': 'Demo',
                    'weight': 1,
                    'region': 'CN',
                    'transport': 'direct',
                    'observed_on': '2026-04-23',
                    'observed_status': 'ok',
                    'home_url': 'https://example.com/'
                }]
            }), encoding='utf-8')
            rc = main(['--config', str(config), '--manual-file', str(Path(tmpdir) / 'missing.json')])
        self.assertEqual(rc, 0)

    def test_invalid_source_returns_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config = Path(tmpdir) / 'config.json'
            manual = Path(tmpdir) / 'manual.json'
            config.write_text(json.dumps({
                'version': 'test',
                'sources': [{
                    'id': 'demo',
                    'label': 'Demo',
                    'weight': 1,
                    'region': 'CN',
                    'transport': 'direct',
                    'observed_on': '2026-04-23',
                    'observed_status': 'ok',
                    'home_url': 'https://example.com/'
                }]
            }), encoding='utf-8')
            manual.write_text(json.dumps({'unknown': ['https://example.com/a']}), encoding='utf-8')
            rc = main(['--config', str(config), '--manual-file', str(manual)])
        self.assertEqual(rc, 1)


if __name__ == '__main__':
    unittest.main()
