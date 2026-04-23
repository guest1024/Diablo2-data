from __future__ import annotations

import unittest

from crawler.check_data_branch_readiness import build_readiness


class CheckDataBranchReadinessTests(unittest.TestCase):
    def test_build_readiness_has_checks_and_ready_flag(self) -> None:
        readiness = build_readiness()
        self.assertIn('checks', readiness)
        self.assertIn('ready', readiness)
        self.assertIn('warnings', readiness)


if __name__ == '__main__':
    unittest.main()
