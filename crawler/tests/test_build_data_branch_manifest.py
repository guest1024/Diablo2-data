from __future__ import annotations

import unittest

from crawler.build_data_branch_manifest import build_manifest


class BuildDataBranchManifestTests(unittest.TestCase):
    def test_build_manifest_has_latest_only_and_files(self) -> None:
        manifest = build_manifest(latest_only=True)
        self.assertIn('latest_only', manifest)
        self.assertIn('files', manifest)
        self.assertTrue(manifest['latest_only'])


if __name__ == '__main__':
    unittest.main()
