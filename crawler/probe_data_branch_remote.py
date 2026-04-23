#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_PATH = REPO_ROOT / 'crawler/state/data-branch-remote-probe.json'


def run_git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(['git', *args], cwd=REPO_ROOT, text=True, capture_output=True)


def build_probe(remote: str = 'origin', branch: str = 'data') -> dict:
    remote_result = run_git('remote', 'get-url', remote)
    remote_exists = remote_result.returncode == 0
    remote_url = remote_result.stdout.strip() if remote_exists else None

    ls_remote = run_git('ls-remote', '--heads', remote, branch)
    accessible = ls_remote.returncode == 0
    branch_exists = bool(ls_remote.stdout.strip()) if accessible else False

    return {
        'remote': remote,
        'branch': branch,
        'remote_exists': remote_exists,
        'remote_url': remote_url,
        'remote_accessible': accessible,
        'branch_exists': branch_exists,
        'stdout': ls_remote.stdout.strip(),
        'stderr': ls_remote.stderr.strip(),
        'returncode': ls_remote.returncode,
    }


def main() -> int:
    probe = build_probe()
    OUT_PATH.write_text(json.dumps(probe, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(probe, ensure_ascii=False, indent=2))
    return 0 if probe['remote_exists'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
