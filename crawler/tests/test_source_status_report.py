from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from crawler.build_source_status_report import build_report


class SourceStatusReportTests(unittest.TestCase):
    def test_build_report_contains_header(self) -> None:
        report = build_report()
        self.assertIn('# Source Status Report', report)
        self.assertIn('| Source | Enabled | Region |', report)

    def test_build_report_mentions_manual_curated_column(self) -> None:
        report = build_report()
        self.assertIn('Manual curated', report)


if __name__ == '__main__':
    unittest.main()
