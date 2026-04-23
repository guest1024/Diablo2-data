from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[2]


def make_service():
    from app.service import Diablo2QAService

    return Diablo2QAService()


def make_test_client() -> TestClient:
    from app.main import app

    return TestClient(app)


def assert_known_backend(testcase: Any, backend: str) -> None:
    testcase.assertIn(
        backend,
        {"local", "postgres", "local-fallback", "postgres-lexical", "postgres-bm25", "postgres-vector", "postgres-hybrid"},
    )


def docker_prefix() -> list[str]:
    if shutil.which("docker") and subprocess.run(["docker", "ps"], capture_output=True, text=True).returncode == 0:
        return []
    if shutil.which("sudo") and subprocess.run(["sudo", "-n", "docker", "ps"], capture_output=True, text=True).returncode == 0:
        return ["sudo", "-n"]
    return []


def maybe_run_psql(sql: str) -> tuple[bool, str]:
    database_url = os.environ.get("DATABASE_URL", "")
    if shutil.which("psql") is not None and database_url:
        completed = subprocess.run(
            ["psql", "-v", "ON_ERROR_STOP=1", database_url, "-At", "-c", sql],
            capture_output=True,
            text=True,
        )
        if completed.returncode == 0:
            return True, completed.stdout.strip()
    prefix = docker_prefix()
    if prefix:
        completed = subprocess.run(
            prefix + ["docker", "exec", "d2-pg17", "/opt/postgresql/bin/psql", "-U", "d2", "-d", "d2", "-At", "-c", sql],
            capture_output=True,
            text=True,
        )
        if completed.returncode == 0:
            return True, completed.stdout.strip()
        return False, completed.stderr.strip() or completed.stdout.strip()
    return False, "psql_not_available"
