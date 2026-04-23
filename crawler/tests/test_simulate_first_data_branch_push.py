from __future__ import annotations

import unittest

from scripts.simulate_first_data_branch_push import BASE_STEPS, REAL_PUSH_STEP


class SimulateFirstDataBranchPushTests(unittest.TestCase):
    def test_preview_is_in_base_steps(self) -> None:
        flattened = [' '.join(step) for step in BASE_STEPS]
        self.assertTrue(any('--preview-only --latest-only' in step for step in flattened))

    def test_real_push_step_defined(self) -> None:
        self.assertIn('--latest-only', ' '.join(REAL_PUSH_STEP))


if __name__ == '__main__':
    unittest.main()
