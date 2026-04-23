#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INCLUDE = [
    'crawler/README.md',
    'crawler/CRAWL_POLICY.md',
    'crawler/OPERATIONS.md',
    'crawler/SOURCE_OPTIONS.md',
    'crawler/VERIFIED_SNAPSHOT_TARGETS.md',
    'crawler/state',
    'crawler/runs',
    'crawler/snapshots',
]
LATEST_RUN_STATE = REPO_ROOT / 'crawler/state/latest-run.json'


def run(
    cmd: list[str],
    *,
    cwd: Path = REPO_ROOT,
    check: bool = True,
    capture_output: bool = False,
    input_text: str | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=cwd,
        check=check,
        text=True,
        capture_output=capture_output,
        input=input_text,
    )


def remote_branch_exists(remote: str, branch: str) -> bool:
    result = run(['git', 'ls-remote', '--heads', remote, branch], capture_output=True)
    return bool(result.stdout.strip())


def load_latest_run_id() -> str | None:
    if not LATEST_RUN_STATE.is_file():
        return None
    payload = json.loads(LATEST_RUN_STATE.read_text(encoding='utf-8'))
    return payload.get('run_id')


def tracked_paths(paths: list[str]) -> list[Path]:
    resolved: list[Path] = []
    for relative in paths:
        path = REPO_ROOT / relative
        if path.exists():
            resolved.append(path)
    return resolved


def build_effective_include(latest_only: bool, explicit_paths: list[str] | None, run_id: str | None) -> list[str]:
    if explicit_paths:
        return explicit_paths
    if not latest_only:
        return DEFAULT_INCLUDE
    include = [
        'crawler/README.md',
        'crawler/CRAWL_POLICY.md',
        'crawler/OPERATIONS.md',
        'crawler/SOURCE_OPTIONS.md',
        'crawler/VERIFIED_SNAPSHOT_TARGETS.md',
        'crawler/state',
        'crawler/snapshots',
    ]
    if run_id:
        include.append(f'crawler/runs/{run_id}')
    return include


def build_publish_preview(paths: list[Path]) -> list[str]:
    preview: list[str] = []
    for path in sorted(paths):
        if path.is_file():
            preview.append(str(path.relative_to(REPO_ROOT)))
        else:
            for child in sorted(path.rglob('*')):
                if child.is_file():
                    preview.append(str(child.relative_to(REPO_ROOT)))
    return preview


def reset_worktree_contents(worktree: Path) -> None:
    for child in worktree.iterdir():
        if child.name == '.git':
            continue
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()


def copy_paths_to_worktree(paths: list[Path], worktree: Path) -> list[str]:
    copied: list[str] = []
    for source in paths:
        relative = source.relative_to(REPO_ROOT)
        target = worktree / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir():
            shutil.copytree(source, target, dirs_exist_ok=True)
        else:
            shutil.copy2(source, target)
        copied.append(str(relative))
    return copied


def ensure_branch_worktree(branch: str, remote: str, worktree: Path) -> str:
    if remote_branch_exists(remote, branch):
        start_point = f'{remote}/{branch}'
        run(['git', 'worktree', 'add', '-B', branch, str(worktree), start_point])
        return start_point

    run(['git', 'worktree', 'add', '--detach', str(worktree), 'HEAD'])
    run(['git', 'checkout', '--orphan', branch], cwd=worktree)
    return 'orphan'


def commit_if_changed(worktree: Path, branch: str, remote: str, commit_message: str, push: bool) -> bool:
    status = run(['git', 'status', '--porcelain'], cwd=worktree, capture_output=True)
    if not status.stdout.strip():
        print('No data-branch changes to commit')
        return False

    run(['git', 'config', 'user.name', 'github-actions[bot]'], cwd=worktree)
    run(['git', 'config', 'user.email', '41898282+github-actions[bot]@users.noreply.github.com'], cwd=worktree)
    run(['git', 'add', '.'], cwd=worktree)
    run(['git', 'commit', '-F', '-'], cwd=worktree, input_text=commit_message)
    if push:
        run(['git', 'push', remote, f'HEAD:{branch}'], cwd=worktree)
    return True


def build_commit_message(run_id: str | None) -> str:
    run_hint = f' for run {run_id}' if run_id else ''
    return f"""Publish crawler snapshot artifacts to the data branch{run_hint}

Keep the repository's data branch focused on crawler-managed snapshot
artifacts so scheduled runs can publish URL-to-snapshot mappings and
captured static pages without mixing them into the main development tree.

Constraint: Data branch should contain crawler-owned outputs only
Constraint: Workflow must tolerate first publish when remote branch does not yet exist
Rejected: Commit crawler artifacts back to the main branch | mixes mutable data with source changes
Confidence: high
Scope-risk: narrow
Reversibility: clean
Directive: Keep the data branch publish set limited to crawler docs/state/runs/snapshots unless the crawler contract changes
Tested: scripts/push_crawler_to_data_branch.py --dry-run
Not-tested: live push to remote in this local session
"""


def main() -> int:
    parser = argparse.ArgumentParser(description='Publish crawler outputs to the data branch')
    parser.add_argument('--branch', default='data')
    parser.add_argument('--remote', default='origin')
    parser.add_argument('--run-id')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--preview-only', action='store_true')
    parser.add_argument('--latest-only', action='store_true', help='publish only the latest run directory plus state/docs/snapshots')
    parser.add_argument('--include', action='append', dest='includes')
    args = parser.parse_args()

    run_id = args.run_id or load_latest_run_id()
    includes = build_effective_include(args.latest_only, args.includes, run_id)
    paths = tracked_paths(includes)
    if not paths:
        raise SystemExit('No crawler paths found to publish')

    print(f'Preparing data-branch publish for branch={args.branch} remote={args.remote}')
    print(f'latest_only={args.latest_only} run_id={run_id}')
    print('Included root paths:')
    for path in paths:
        print(f' - {path.relative_to(REPO_ROOT)}')

    preview = build_publish_preview(paths)
    print('Preview file list:')
    for item in preview[:200]:
        print(f' - {item}')
    if len(preview) > 200:
        print(f' ... ({len(preview) - 200} more files)')

    if args.preview_only:
        print('Preview only: skipping worktree creation and git push')
        return 0
    if args.dry_run:
        print('Dry run: skipping worktree creation and git push')
        return 0

    worktree: Path | None = None
    try:
        with tempfile.TemporaryDirectory(prefix='crawler-data-branch-') as tmpdir:
            worktree = Path(tmpdir) / 'worktree'
            start_point = ensure_branch_worktree(args.branch, args.remote, worktree)
            print(f'Using start point: {start_point}')
            reset_worktree_contents(worktree)
            copied = copy_paths_to_worktree(paths, worktree)
            print('Copied root paths into worktree:')
            for item in copied:
                print(f' - {item}')
            commit_if_changed(
                worktree,
                branch=args.branch,
                remote=args.remote,
                commit_message=build_commit_message(run_id),
                push=True,
            )
    finally:
        if worktree and worktree.exists():
            run(['git', 'worktree', 'remove', '--force', str(worktree)], check=False)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
