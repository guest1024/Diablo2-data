from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import crawler.manage_manual_curated_urls as manager


class ManageManualCuratedUrlsTests(unittest.TestCase):
    def test_add_and_remove_url(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            manual = Path(tmpdir) / 'manual.json'
            config = Path(tmpdir) / 'sources.json'
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
            with patch.object(manager, 'MANUAL_PATH', manual), patch.object(manager, 'CONFIG_PATH', config):
                manager.add_url('demo', 'https://example.com/a')
                payload = json.loads(manual.read_text(encoding='utf-8'))
                self.assertEqual(payload['demo'], ['https://example.com/a'])
                manager.remove_url('demo', 'https://example.com/a')
                payload = json.loads(manual.read_text(encoding='utf-8'))
                self.assertEqual(payload['demo'], [])


if __name__ == '__main__':
    unittest.main()
