from __future__ import annotations

import unittest

from scripts.build_crawler_reports import COMMANDS


class BuildCrawlerReportsTests(unittest.TestCase):
    def test_contains_expected_export_commands(self) -> None:
        flattened = [" ".join(command) for command in COMMANDS]
        self.assertTrue(any("export_snapshot_relations.py" in command for command in flattened))
        self.assertTrue(any("build_data_branch_manifest.py" in command for command in flattened))


if __name__ == "__main__":
    unittest.main()
