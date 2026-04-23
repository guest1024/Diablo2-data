from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import crawler.export_page_records as export_module
from crawler.storage import write_json


class ExportPageRecordsTests(unittest.TestCase):
    def test_main_writes_one_file_per_catalog_entry_and_prunes_stale_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            state = root / 'state'
            state.mkdir()
            write_json(
                state / 'page_catalog.json',
                {
                    '91d2::https://a.com/guide': {
                        'source_id': '91d2',
                        'source_label': '91D2',
                        'url': 'https://a.com/guide',
                        'content_type': 'text/html',
                    }
                },
            )
            stale_dir = state / 'page-records' / '91d2'
            stale_dir.mkdir(parents=True)
            stale_file = stale_dir / 'old.json'
            stale_file.write_text('{}\n', encoding='utf-8')

            with (
                patch.object(export_module, 'CURRENT_DIR', root),
                patch.object(export_module, 'CATALOG_PATH', state / 'page_catalog.json'),
                patch.object(export_module, 'OUT_DIR', state / 'page-records'),
                patch.object(export_module, 'INDEX_PATH', state / 'page-records' / 'index.json'),
            ):
                export_module.main()

            record_path = state / 'page-records' / '91d2' / 'a.com' / 'guide' / 'index.json'
            self.assertTrue(record_path.is_file())
            payload = json.loads(record_path.read_text(encoding='utf-8'))
            self.assertEqual(payload['catalog_key'], '91d2::https://a.com/guide')
            self.assertFalse(stale_file.exists())


if __name__ == '__main__':
    unittest.main()
