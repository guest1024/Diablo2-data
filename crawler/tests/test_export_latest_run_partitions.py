from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import crawler.export_latest_run_partitions as export_module


class ExportLatestRunPartitionsTests(unittest.TestCase):
    def test_build_payload_extracts_summary_and_sources(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            latest = Path(tmpdir) / 'latest-run.json'
            latest.write_text(json.dumps({
                'run_id': 'run-1',
                'generated_at': 'now',
                'sources': [{'id': '91d2'}],
            }), encoding='utf-8')
            with patch.object(export_module, 'LATEST_RUN_PATH', latest):
                payload = export_module.build_payload()
        self.assertEqual(payload['summary']['run_id'], 'run-1')
        self.assertEqual(payload['sources'][0]['id'], '91d2')


if __name__ == '__main__':
    unittest.main()
