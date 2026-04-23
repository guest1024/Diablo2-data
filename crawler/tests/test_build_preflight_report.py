from __future__ import annotations

import unittest

from crawler.build_preflight_report import build_report


class BuildPreflightReportTests(unittest.TestCase):
    def test_build_report_has_readiness_and_latest_run(self) -> None:
        report = build_report()
        self.assertIn('latest_run_id', report)
        self.assertIn('readiness', report)


if __name__ == '__main__':
    unittest.main()
