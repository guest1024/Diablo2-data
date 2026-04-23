from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import crawler.build_final_push_summary as summary_module


class BuildFinalPushSummaryTests(unittest.TestCase):
    def test_main_writes_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            out = Path(tmpdir) / 'summary.md'
            readiness = Path(tmpdir) / 'readiness.json'
            preflight = Path(tmpdir) / 'preflight.json'
            readiness.write_text('{"ready": true, "warnings": ["warn-1"]}', encoding='utf-8')
            preflight.write_text('{"latest_run_id": "run-1", "snapshot_relation_count": 3, "remote_probe": {"branch_exists": false}}', encoding='utf-8')
            with patch.object(summary_module, 'OUT_PATH', out), patch.object(summary_module, 'READINESS', readiness), patch.object(summary_module, 'PREFLIGHT', preflight):
                rc = summary_module.main()
            self.assertEqual(rc, 0)
            self.assertIn('run-1', out.read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
