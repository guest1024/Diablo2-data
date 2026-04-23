#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

LATEST = Path(__file__).resolve().parents[1] / 'crawler/state/latest-run.json'


def main() -> int:
    payload = json.loads(LATEST.read_text(encoding='utf-8'))
    print(payload['run_id'])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
