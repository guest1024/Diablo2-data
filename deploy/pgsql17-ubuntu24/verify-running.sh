#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/../.." && pwd)
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
  "$@"
}

run "${DOCKER_PREFIX[@]}" "$DOCKER_COMPOSE_BIN" -f "$COMPOSE_FILE" ps
run "${DOCKER_PREFIX[@]}" docker inspect d2-pg17 --format 'status={{.State.Status}} health={{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}} started={{.State.StartedAt}}'
run "${DOCKER_PREFIX[@]}" docker exec d2-pg17 /opt/postgresql/bin/psql -U d2 -d d2 -At -c 'SELECT extname FROM pg_extension ORDER BY extname;'
run "${DOCKER_PREFIX[@]}" docker exec d2-pg17 /opt/postgresql/bin/psql -U d2 -d d2 -At -c 'SELECT count(*) FROM d2.documents;'
run "${DOCKER_PREFIX[@]}" docker exec d2-pg17 /opt/postgresql/bin/psql -U d2 -d d2 -At -c 'SELECT count(*) FROM d2.canonical_entities;'
run "${DOCKER_PREFIX[@]}" docker exec d2-pg17 /opt/postgresql/bin/psql -U d2 -d d2 -At -c 'SELECT count(*) FROM d2.canonical_claims;'
run "${DOCKER_PREFIX[@]}" docker exec d2-pg17 /opt/postgresql/bin/psql -U d2 -d d2 -At -c 'SELECT count(*) FROM d2.provenance;'
run "${DOCKER_PREFIX[@]}" docker exec d2-pg17 /opt/postgresql/bin/psql -U d2 -d d2 -At -c 'SELECT count(*) FROM d2.strategy_edge_facts;'
