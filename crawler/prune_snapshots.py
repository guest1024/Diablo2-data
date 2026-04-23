#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from crawler.catalog import load_page_catalog
from crawler.storage import write_json

RUNS_DIR = CURRENT_DIR / 'runs'
SNAPSHOTS_DIR = CURRENT_DIR / 'snapshots'
CATALOG_PATH = CURRENT_DIR / 'state/page_catalog.json'


PRUNABLE_CATALOG_CAPTURE_STATUSES = {'filtered', 'catalog-only'}


def list_run_dirs() -> list[Path]:
    if not RUNS_DIR.is_dir():
        return []
    return sorted([path for path in RUNS_DIR.iterdir() if path.is_dir()])


def snapshot_paths_from_catalog(catalog: dict[str, dict]) -> set[Path]:
    paths: set[Path] = set()
    for row in catalog.values():
        snapshot_path = row.get('snapshot_path')
        if snapshot_path:
            paths.add(CURRENT_DIR / snapshot_path)
    return paths


def display_relative(path: Path, root: Path) -> str:
    if path.is_relative_to(root):
        return str(path.relative_to(root))
    if len(path.parents) >= 3:
        return str(path.relative_to(path.parents[2]))
    return str(path)


def prune_runs(keep: int, dry_run: bool) -> list[str]:
    run_dirs = list_run_dirs()
    if keep < 0:
        keep = 0
    removable = run_dirs[:-keep] if keep and len(run_dirs) > keep else ([] if keep else run_dirs)
    removed: list[str] = []
    for path in removable:
        removed.append(display_relative(path, RUNS_DIR.parent))
        if not dry_run:
            shutil.rmtree(path)
    return removed


def prune_catalog_without_snapshots(catalog: dict[str, dict], dry_run: bool) -> tuple[dict[str, dict], list[str]]:
    kept: dict[str, dict] = {}
    removed: list[str] = []
    for key, row in catalog.items():
        capture_status = row.get('capture_status')
        snapshot_path = row.get('snapshot_path')
        if not snapshot_path and capture_status in PRUNABLE_CATALOG_CAPTURE_STATUSES:
            removed.append(key)
            continue
        kept[key] = row
    if not dry_run and removed:
        write_json(CATALOG_PATH, kept)
    return kept, removed


def prune_unreferenced_snapshots(catalog: dict[str, dict], dry_run: bool) -> list[str]:
    referenced = snapshot_paths_from_catalog(catalog)
    removed: list[str] = []
    if not SNAPSHOTS_DIR.is_dir():
        return removed
    for path in sorted(SNAPSHOTS_DIR.rglob('*')):
        if not path.is_file():
            continue
        if path not in referenced:
            removed.append(display_relative(path, SNAPSHOTS_DIR.parent))
            if not dry_run:
                path.unlink()
    if not dry_run:
        for directory in sorted(SNAPSHOTS_DIR.rglob('*'), reverse=True):
            if directory.is_dir() and not any(directory.iterdir()):
                directory.rmdir()
    return removed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Prune old crawler runs and unreferenced snapshots')
    parser.add_argument('--keep-runs', type=int, default=10, help='number of most recent run directories to keep')
    parser.add_argument('--prune-snapshots', action='store_true', help='delete snapshot files not referenced by page_catalog.json')
    parser.add_argument('--prune-catalog-without-snapshots', action='store_true', help='drop catalog rows that were filtered/noise and never produced a snapshot')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args(argv)

    catalog = load_page_catalog(CATALOG_PATH)
    current_catalog = catalog
    removed_catalog_rows: list[str] = []
    if args.prune_catalog_without_snapshots:
        current_catalog, removed_catalog_rows = prune_catalog_without_snapshots(catalog, args.dry_run)

    removed_runs = prune_runs(args.keep_runs, args.dry_run)
    removed_snapshots = prune_unreferenced_snapshots(current_catalog, args.dry_run) if args.prune_snapshots else []

    print(json.dumps(
        {
            'dry_run': args.dry_run,
            'removed_runs': removed_runs,
            'removed_snapshots': removed_snapshots,
            'removed_catalog_rows': removed_catalog_rows,
            'keep_runs': args.keep_runs,
            'prune_snapshots': args.prune_snapshots,
            'prune_catalog_without_snapshots': args.prune_catalog_without_snapshots,
        },
        ensure_ascii=False,
        indent=2,
    ))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
