from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import crawler.export_source_health_partitions as export_module


class ExportSourceHealthPartitionsTests(unittest.TestCase):
    def test_build_rows_reads_sources(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / 'source-health.json'
            path.write_text(json.dumps({'sources': [{'id': '91d2'}, {'id': '17173'}]}), encoding='utf-8')
            with patch.object(export_module, 'HEALTH_PATH', path):
                rows = export_module.build_rows()
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]['id'], '91d2')


if __name__ == '__main__':
    unittest.main()
