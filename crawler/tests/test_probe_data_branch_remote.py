from __future__ import annotations

import unittest
from unittest.mock import patch

import crawler.probe_data_branch_remote as probe_module


class ProbeDataBranchRemoteTests(unittest.TestCase):
    def test_build_probe_returns_expected_keys(self) -> None:
        class Result:
            def __init__(self, returncode: int, stdout: str = '', stderr: str = '') -> None:
                self.returncode = returncode
                self.stdout = stdout
                self.stderr = stderr

        calls = []

        def fake_run_git(*args: str):
            calls.append(args)
            if args[:2] == ('remote', 'get-url'):
                return Result(0, 'git@github.com:demo/repo.git\n')
            return Result(0, 'abc\trefs/heads/data\n')

        with patch.object(probe_module, 'run_git', fake_run_git):
            probe = probe_module.build_probe()
        self.assertTrue(probe['remote_exists'])
        self.assertTrue(probe['remote_accessible'])
        self.assertTrue(probe['branch_exists'])
        self.assertIn(('remote', 'get-url', 'origin'), calls)


if __name__ == '__main__':
    unittest.main()
