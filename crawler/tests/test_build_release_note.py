from __future__ import annotations

import unittest

from crawler.build_release_note import main


class BuildReleaseNoteTests(unittest.TestCase):
    def test_main_runs(self) -> None:
        rc = main()
        self.assertEqual(rc, 0)


if __name__ == '__main__':
    unittest.main()
