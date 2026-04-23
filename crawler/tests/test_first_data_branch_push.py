from __future__ import annotations

import unittest

from scripts.first_data_branch_push import PRECHECK_STEPS, REAL_PUSH_STEP


class FirstDataBranchPushTests(unittest.TestCase):
    def test_precheck_contains_preview(self) -> None:
        flattened = [' '.join(step) for step in PRECHECK_STEPS]
        self.assertTrue(any('--preview-only --latest-only' in step for step in flattened))

    def test_real_push_is_separate(self) -> None:
        self.assertIn('--latest-only', ' '.join(REAL_PUSH_STEP))
        self.assertNotIn('--preview-only', ' '.join(REAL_PUSH_STEP))


if __name__ == '__main__':
    unittest.main()
