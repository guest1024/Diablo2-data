#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON = ROOT / '.venv' / 'bin' / 'python'
PIP = ROOT / '.venv' / 'bin' / 'pip'


def main() -> int:
    if not PYTHON.exists() or not PIP.exists():
        raise SystemExit('FAIL: .venv is missing; create the virtualenv first.')
    subprocess.run([str(PIP), 'install', 'psycopg[binary]>=3.2,<4'], check=True)
    print('PASS: psycopg installed into .venv')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
