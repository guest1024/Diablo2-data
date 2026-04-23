from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from crawler.models import FetchResponse
from crawler.probe_manual_curated_urls import build_probe_report


class ProbeManualCuratedUrlsTests(unittest.TestCase):
    def test_build_probe_report_uses_manual_urls(self) -> None:
        payload = {
            'version': 'test',
            'user_agent': 'ua',
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
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            config = Path(tmpdir) / 'config.json'
            manual = Path(tmpdir) / 'manual.json'
            config.write_text(json.dumps(payload), encoding='utf-8')
            manual.write_text(json.dumps({'demo': ['https://example.com/a']}), encoding='utf-8')

            def fake_fetch(url: str) -> FetchResponse:
                return FetchResponse(url=url, status=200, content_type='text/html', body=b'<title>ok</title>')

            report = build_probe_report(config, manual, fetch=fake_fetch)
        self.assertEqual(report['url_count'], 1)
        self.assertEqual(report['ok_count'], 1)
        self.assertEqual(report['rows'][0]['title'], 'ok')


if __name__ == '__main__':
    unittest.main()
