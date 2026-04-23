from __future__ import annotations

import unittest

from crawler.build_state_index import build_index


class BuildStateIndexTests(unittest.TestCase):
    def test_build_index_has_reports_and_partitions(self) -> None:
        payload = build_index()
        self.assertIn('reports', payload)
        self.assertIn('partitions', payload)
        self.assertIn('single_files', payload)
        self.assertIn('final_push_summary', payload['reports'])
        self.assertIn('latest_run', payload['partitions'])


if __name__ == '__main__':
    unittest.main()
