from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


DEFAULT_CONTAINER = os.environ.get("PG_DOCKER_CONTAINER", "d2-pg17")
DEFAULT_DB = os.environ.get("PGDATABASE", "d2")
DEFAULT_USER = os.environ.get("PGUSER", "d2")


def _docker_prefix() -> list[str] | None:
    if shutil.which("docker") and subprocess.run(["docker", "ps"], capture_output=True, text=True).returncode == 0:
        return []
    if shutil.which("sudo") and subprocess.run(["sudo", "-n", "docker", "ps"], capture_output=True, text=True).returncode == 0:
        return ["sudo", "-n"]
    return None


def has_local_psql() -> bool:
    return shutil.which("psql") is not None


def can_use_docker_psql(container_name: str = DEFAULT_CONTAINER) -> bool:
    prefix = _docker_prefix()
    if prefix is None:
        return False
    completed = subprocess.run(
        prefix + ["docker", "ps", "-q", "--filter", f"name={container_name}"],
        capture_output=True,
        text=True,
    )
    return completed.returncode == 0 and bool(completed.stdout.strip())


def ensure_psql_access(container_name: str = DEFAULT_CONTAINER) -> None:
    if has_local_psql() or can_use_docker_psql(container_name=container_name):
        return
    raise SystemExit(
        "FAIL: neither local psql nor docker exec psql is available. "
        "Install PostgreSQL client tools or start the d2-pg17 container first."
    )


def run_psql_file(
    path: Path,
    *,
    database_url: str | None = None,
    container_name: str = DEFAULT_CONTAINER,
    db_name: str = DEFAULT_DB,
    db_user: str = DEFAULT_USER,
) -> None:
    if has_local_psql():
        cmd = ["psql", "-v", "ON_ERROR_STOP=1"]
        if database_url:
            cmd.append(database_url)
        cmd.extend(["-f", str(path)])
        subprocess.run(cmd, check=True)
        return

    if can_use_docker_psql(container_name=container_name):
        prefix = _docker_prefix()
        if prefix is None:
            ensure_psql_access(container_name=container_name)
        subprocess.run(
            prefix
            + [
                "docker",
                "exec",
                container_name,
                "/opt/postgresql/bin/psql",
                "-v",
                "ON_ERROR_STOP=1",
                "-U",
                db_user,
                "-d",
                db_name,
                "-f",
                str(path),
            ],
            check=True,
        )
        return

    ensure_psql_access(container_name=container_name)
