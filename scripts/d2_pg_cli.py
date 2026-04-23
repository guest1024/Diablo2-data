#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable

COMMAND_GROUPS: dict[str, list[list[str]]] = {
    'fetch-tier0': [
        [PYTHON, 'scripts/fetch_tier0.py', '--timeout', '8'],
        [PYTHON, 'scripts/verify_tier0_fetch.py'],
    ],
    'normalize-tier0': [
        [PYTHON, 'scripts/normalize_tier0.py'],
        [PYTHON, 'scripts/verify_tier0_normalization.py'],
    ],
    'merge-production': [
        [PYTHON, 'scripts/build_merged_normalized.py'],
        [PYTHON, 'scripts/build_chroma_package.py'],
        [PYTHON, 'scripts/build_graph_support_assets.py'],
        [PYTHON, 'scripts/verify_graph_support_assets.py'],
    ],
    'structured-support': [
        [PYTHON, 'scripts/build_structured_support_assets.py'],
        [PYTHON, 'scripts/verify_structured_support_assets.py'],
    ],
    'pg-bundle': [
        [PYTHON, 'scripts/build_postgres_bundle.py'],
        [PYTHON, 'scripts/verify_postgres_bundle.py'],
    ],
    'pg-dict-bundle': [
        [PYTHON, 'scripts/build_pg_dict_bundle.py'],
        [PYTHON, 'scripts/verify_pg_dict_bundle.py'],
    ],
    'runtime-verify': [
        [PYTHON, 'scripts/verify_query_execution_chain.py'],
    ],
}

PIPELINES: dict[str, list[str]] = {
    'site-to-chunks': ['fetch-tier0', 'normalize-tier0', 'merge-production'],
    'site-to-pg-assets': ['fetch-tier0', 'normalize-tier0', 'merge-production', 'structured-support', 'pg-bundle', 'pg-dict-bundle'],
    'refresh-pg-search': ['merge-production', 'structured-support', 'pg-bundle', 'pg-dict-bundle', 'runtime-verify'],
}


def run_commands(commands: list[list[str]], dry_run: bool = False) -> int:
    for command in commands:
        print('==>', ' '.join(command))
        if dry_run:
            continue
        completed = subprocess.run(command, cwd=ROOT)
        if completed.returncode != 0:
            return completed.returncode
    return 0


def flatten_pipeline(stages: list[str]) -> list[list[str]]:
    commands: list[list[str]] = []
    for stage in stages:
        commands.extend(COMMAND_GROUPS[stage])
    return commands


def main() -> int:
    parser = argparse.ArgumentParser(
        description='Diablo II PostgreSQL pipeline CLI: from site fetch to chunk schema to PostgreSQL bundles.'
    )
    subparsers = parser.add_subparsers(dest='command', required=True)

    stage_parser = subparsers.add_parser('stage', help='Run one named stage group.')
    stage_parser.add_argument('name', choices=sorted(COMMAND_GROUPS.keys()))
    stage_parser.add_argument('--dry-run', action='store_true')

    pipeline_parser = subparsers.add_parser('pipeline', help='Run a multi-stage pipeline.')
    pipeline_parser.add_argument('name', choices=sorted(PIPELINES.keys()))
    pipeline_parser.add_argument('--dry-run', action='store_true')

    load_pg_parser = subparsers.add_parser('load-pg', help='Load PostgreSQL bundle into a database using psql.')
    load_pg_parser.add_argument('--database-url', default=None)
    load_pg_parser.add_argument('--with-vector', action='store_true')
    load_pg_parser.add_argument('--skip-build', action='store_true')

    load_dict_parser = subparsers.add_parser('load-dict', help='Load dictionary/query-understanding bundle into PostgreSQL using psql.')
    load_dict_parser.add_argument('--database-url', default=None)
    load_dict_parser.add_argument('--skip-build', action='store_true')

    subparsers.add_parser('show-plan', help='Show available stages and pipelines.')

    args = parser.parse_args()

    if args.command == 'stage':
        return run_commands(COMMAND_GROUPS[args.name], dry_run=args.dry_run)
    if args.command == 'pipeline':
        return run_commands(flatten_pipeline(PIPELINES[args.name]), dry_run=args.dry_run)
    if args.command == 'load-pg':
        command = [PYTHON, 'scripts/load_postgres_bundle.py']
        if args.database_url:
            command.extend(['--database-url', args.database_url])
        if args.with_vector:
            command.append('--with-vector')
        if args.skip_build:
            command.append('--skip-bundle-build')
        return run_commands([command])
    if args.command == 'load-dict':
        command = [PYTHON, 'scripts/load_pg_dict_bundle.py']
        if args.database_url:
            command.extend(['--database-url', args.database_url])
        if args.skip_build:
            command.append('--skip-bundle-build')
        return run_commands([command])
    if args.command == 'show-plan':
        print('Available stages:')
        for name, commands in sorted(COMMAND_GROUPS.items()):
            print(f'- {name}')
            for command in commands:
                print(f'    {" ".join(command)}')
        print('\nAvailable pipelines:')
        for name, stages in sorted(PIPELINES.items()):
            print(f'- {name}: {" -> ".join(stages)}')
        return 0

    return 1


if __name__ == '__main__':
    raise SystemExit(main())
