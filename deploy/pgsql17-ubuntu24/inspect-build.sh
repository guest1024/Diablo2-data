#!/usr/bin/env bash
set -euo pipefail

if command -v sudo >/dev/null 2>&1 && sudo -n docker info >/dev/null 2>&1; then
  DOCKER_PREFIX=(sudo -n)
else
  DOCKER_PREFIX=()
fi

CONTAINER_ID=$(${DOCKER_PREFIX[@]} docker ps -q --filter ancestor=5905b9a8ed60 | head -n 1)
if [[ -z "$CONTAINER_ID" ]]; then
  echo 'No active PostgreSQL source-build container found.'
  exit 0
fi

echo "Build container: $CONTAINER_ID"
${DOCKER_PREFIX[@]} docker inspect "$CONTAINER_ID" --format 'status={{.State.Status}} running={{.State.Running}} started={{.State.StartedAt}}'
${DOCKER_PREFIX[@]} docker exec "$CONTAINER_ID" ps -eo pid,ppid,%cpu,%mem,etime,cmd | sed -n '1,30p'
