#!/usr/bin/env python3
from __future__ import annotations

from run_unittest_case import run_case
from tests.test_postgres_runtime import PostgresRuntimeTest


if __name__ == "__main__":
    raise SystemExit(run_case(PostgresRuntimeTest))
