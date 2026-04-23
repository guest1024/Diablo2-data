from __future__ import annotations

import unittest

from crawler.reporting import build_catalog_summary, filter_catalog_rows


class ReportingTests(unittest.TestCase):
    def test_filter_catalog_rows(self) -> None:
        catalog = {
            'a': {'source_id': '91d2', 'capture_status': 'saved', 'lifecycle_status': 'new', 'url': 'u1'},
            'b': {'source_id': '91d2', 'capture_status': 'frozen', 'lifecycle_status': 'frozen', 'url': 'u2'},
            'c': {'source_id': '17173', 'capture_status': 'saved', 'lifecycle_status': 'updated', 'url': 'u3'},
        }
        rows = filter_catalog_rows(catalog, source_id='91d2', capture_status='saved')
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['url'], 'u1')

    def test_filter_catalog_rows_snapshot_only(self) -> None:
        catalog = {
            'a': {'source_id': '91d2', 'capture_status': 'saved', 'lifecycle_status': 'new', 'url': 'u1', 'snapshot_path': 'snapshots/a.html'},
            'b': {'source_id': '91d2', 'capture_status': 'filtered', 'lifecycle_status': 'ignored', 'url': 'u2'},
        }
        rows = filter_catalog_rows(catalog, snapshot_only=True)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['url'], 'u1')

    def test_build_catalog_summary(self) -> None:
        rows = [
            {'source_id': '91d2', 'capture_status': 'saved', 'lifecycle_status': 'new'},
            {'source_id': '91d2', 'capture_status': 'frozen', 'lifecycle_status': 'frozen'},
            {'source_id': '17173', 'capture_status': 'saved', 'lifecycle_status': 'updated'},
        ]
        summary = build_catalog_summary(rows)
        self.assertEqual(summary['total'], 3)
        self.assertEqual(summary['capture']['saved'], 2)
        self.assertEqual(summary['by_source']['91d2']['count'], 2)


if __name__ == '__main__':
    unittest.main()
