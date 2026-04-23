#!/usr/bin/env bash
set -euo pipefail

process_file() {
  local file="$1"
  case "$file" in
    *.sh)
      echo "[init] running shell script: $file"
      bash "$file"
      ;;
    *.sql)
      echo "[init] running sql file: $file"
      psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -f "$file"
      ;;
    *)
      echo "[init] ignoring file: $file"
      ;;
  esac
}

for file in /docker-entrypoint-initdb.d/*; do
  [ -e "$file" ] || continue
  process_file "$file"
done
