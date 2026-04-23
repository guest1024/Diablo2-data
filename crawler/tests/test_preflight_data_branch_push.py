from __future__ import annotations

import unittest

from scripts.preflight_data_branch_push import STEPS


class PreflightDataBranchPushTests(unittest.TestCase):
    def test_preview_step_present(self) -> None:
        flattened = [" ".join(step) for step in STEPS]
        self.assertTrue(any("push_crawler_to_data_branch.py --branch data --remote origin --preview-only --latest-only" in step for step in flattened))


if __name__ == "__main__":
    unittest.main()
