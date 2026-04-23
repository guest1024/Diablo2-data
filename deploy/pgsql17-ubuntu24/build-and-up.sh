#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/../.." && pwd)
PYTHON=${PYTHON:-$ROOT/.venv/bin/python}
if [[ ! -x "$PYTHON" ]]; then
  PYTHON=${PYTHON:-python3}
fi

DRY_RUN=${DRY_RUN:-false}
COMPOSE_FILE="$ROOT/deploy/pgsql17-ubuntu24/docker-compose.yml"
DOCKER_COMPOSE_BIN=${DOCKER_COMPOSE_BIN:-docker-compose}
DOCKER_PREFIX=()

if command -v sudo >/dev/null 2>&1; then
  if ! docker info >/dev/null 2>&1; then
    if sudo -n docker info >/dev/null 2>&1; then
      DOCKER_PREFIX=(sudo -n)
    fi
  fi
fi

run() {
  echo "==> $*"
  if [[ "$DRY_RUN" == "true" ]]; then
    return 0
  fi
  "$@"
}

run "$PYTHON" "$ROOT/scripts/build_postgres_bundle.py"
run "$PYTHON" "$ROOT/scripts/build_pg_dict_bundle.py"
run "$PYTHON" "$ROOT/scripts/build_pg_embedding_bundle.py"
run "$PYTHON" "$ROOT/scripts/build_pg_strategy_bundle.py"
run "${DOCKER_PREFIX[@]}" "$DOCKER_COMPOSE_BIN" -f "$COMPOSE_FILE" build --pull
run "${DOCKER_PREFIX[@]}" "$DOCKER_COMPOSE_BIN" -f "$COMPOSE_FILE" up -d
run "${DOCKER_PREFIX[@]}" "$DOCKER_COMPOSE_BIN" -f "$COMPOSE_FILE" ps
run bash "$ROOT/deploy/pgsql17-ubuntu24/verify-running.sh"
