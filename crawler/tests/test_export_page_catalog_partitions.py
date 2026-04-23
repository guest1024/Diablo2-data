from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import crawler.export_page_catalog_partitions as export_module
from crawler.storage import write_json


class ExportPageCatalogPartitionsTests(unittest.TestCase):
    def test_build_partition_rows_reads_catalog(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            state = root / 'state'
            state.mkdir()
            write_json(state / 'page_catalog.json', {
                'a': {'source_id': '91d2', 'url': 'https://a.com'},
                'b': {'source_id': '17173', 'url': 'https://b.com'},
            })
            with patch.object(export_module, 'CATALOG_PATH', state / 'page_catalog.json'):
                rows = export_module.build_partition_rows()
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]['catalog_key'], 'b')


if __name__ == '__main__':
    unittest.main()
