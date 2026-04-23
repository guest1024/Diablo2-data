#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TRACKED_PATHS = [
    'crawler',
    '.github/workflows/scheduler.yml',
    'scripts/push_crawler_to_data_branch.py',
]
COMMIT_MESSAGE = """Keep crawler workflow metadata aligned with scheduled snapshot execution

The scheduled workflow updates crawler-maintained metadata files and the
workflow/reporting surfaces that describe recent snapshot activity.

Constraint: Source branch commits should stay limited to workflow and crawler metadata
Rejected: Skip source-branch metadata commits entirely | loses operational traceability in the main branch
Confidence: high
Scope-risk: narrow
Reversibility: clean
Directive: Keep source-branch commits focused on crawler code/docs/workflow, and publish raw snapshot artifacts to the data branch separately
Tested: crawler/run_tests.py; crawler/verify_framework.py
Not-tested: live GitHub Actions execution in this local session
"""


def run(cmd: list[str], *, capture: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=REPO_ROOT, text=True, capture_output=capture, check=True)


def has_changes() -> bool:
    result = run(['git', 'status', '--porcelain', '--', *TRACKED_PATHS], capture=True)
    return bool(result.stdout.strip())


def main() -> int:
    if not has_changes():
        print('No crawler metadata changes to commit')
        return 0

    run(['git', 'config', 'user.name', 'github-actions[bot]'])
    run(['git', 'config', 'user.email', '41898282+github-actions[bot]@users.noreply.github.com'])
    run(['git', 'add', *TRACKED_PATHS])
    subprocess.run(
        ['git', 'commit', '-F', '-'],
        cwd=REPO_ROOT,
        text=True,
        input=COMMIT_MESSAGE,
        check=True,
    )
    branch = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.strip()
    run(['git', 'pull', '--rebase', 'origin', branch])
    run(['git', 'push', 'origin', f'HEAD:{branch}'])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
