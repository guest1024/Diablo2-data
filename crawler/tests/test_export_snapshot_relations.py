from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import crawler.export_snapshot_relations as export_module
from crawler.storage import write_json


class ExportSnapshotRelationsTests(unittest.TestCase):
    def test_build_snapshot_relations_filters_missing_snapshot_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            state = root / 'state'
            state.mkdir()
            write_json(
                state / 'page_catalog.json',
                {
                    'a': {'source_id': '91d2', 'url': 'https://a', 'snapshot_path': 'snapshots/a.html', 'title': 'A'},
                    'b': {'source_id': '91d2', 'url': 'https://b', 'title': 'B'},
                },
            )
            with patch.object(export_module, 'CURRENT_DIR', root), patch.object(export_module, 'CATALOG_PATH', state / 'page_catalog.json'):
                rows = export_module.build_snapshot_relations()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['url'], 'https://a')


if __name__ == '__main__':
    unittest.main()
