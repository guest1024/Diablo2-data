from __future__ import annotations

import unittest

from crawler.build_manual_curated_backlog import build_backlog_report


class ManualCuratedBacklogTests(unittest.TestCase):
    def test_backlog_report_contains_header(self) -> None:
        report = build_backlog_report()
        self.assertIn('# Manual Curated Backlog', report)
        self.assertIn('| Source | Enabled | Transport |', report)

    def test_backlog_report_contains_suggested_action(self) -> None:
        report = build_backlog_report()
        self.assertIn('Suggested action', report)


if __name__ == '__main__':
    unittest.main()
