#!/usr/bin/env bash
set -euo pipefail

export PG_HOME="${PG_HOME:-/opt/postgresql}"
export PATH="$PG_HOME/bin:$PATH"
export PGDATA="${PGDATA:-/var/lib/postgresql/data}"
export POSTGRES_USER="${POSTGRES_USER:-d2}"
export POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-d2pass}"
export POSTGRES_DB="${POSTGRES_DB:-d2}"
export AUTO_LOAD_APP_SCHEMA="${AUTO_LOAD_APP_SCHEMA:-true}"
export AUTO_LOAD_BUNDLES="${AUTO_LOAD_BUNDLES:-true}"
export PGPORT="${PGPORT:-5432}"

if [[ "${1:-postgres}" == "postgres" ]] && [[ "$(id -u)" == "0" ]]; then
  mkdir -p "$PGDATA" /var/run/postgresql
  chown -R postgres:postgres "$PGDATA" /var/run/postgresql /docker-entrypoint-initdb.d /bootstrap || true
  exec gosu postgres "$0" "$@"
fi

if [[ "${1:-postgres}" != "postgres" ]]; then
  exec "$@"
fi

mkdir -p "$PGDATA"
chmod 700 "$PGDATA"

if [[ ! -s "$PGDATA/PG_VERSION" ]]; then
  echo "[entrypoint] initializing database cluster at $PGDATA"
  pwfile=$(mktemp)
  trap 'rm -f "$pwfile"' EXIT
  printf '%s' "$POSTGRES_PASSWORD" > "$pwfile"
  initdb -D "$PGDATA" --username="$POSTGRES_USER" --pwfile="$pwfile" --encoding=UTF8 --locale=C.UTF-8

  cp "$PG_HOME/share/postgresql.conf.template" "$PGDATA/postgresql.conf"
  {
    echo "host all all all scram-sha-256"
    echo "host replication all all scram-sha-256"
  } >> "$PGDATA/pg_hba.conf"

  pg_ctl -D "$PGDATA" -o "-c listen_addresses='localhost' -p $PGPORT" -w start

  if ! psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname postgres -At -c "SELECT 1 FROM pg_database WHERE datname = '$POSTGRES_DB';" | grep -q 1; then
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname postgres -c "CREATE DATABASE \"$POSTGRES_DB\";"
  fi

  if [[ "$AUTO_LOAD_APP_SCHEMA" == "true" ]]; then
    if [[ -d /bootstrap/sql/postgres ]]; then
      for file in \
        /bootstrap/sql/postgres/001_core_schema.sql \
        /bootstrap/sql/postgres/002_optional_vector.sql \
        /bootstrap/sql/postgres/003_views.sql \
        /bootstrap/sql/postgres/004_dict_query_quality_schema.sql \
        /bootstrap/sql/postgres/005_dict_query_quality_views.sql \
        /bootstrap/sql/postgres/006_pg_textsearch_indexes.sql \
        /bootstrap/sql/postgres/007_strategy_views.sql; do
        if [[ -f "$file" ]]; then
          echo "[entrypoint] applying schema file $file"
          psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -f "$file"
        fi
      done
    fi
  fi

  /usr/local/bin/process-init-files.sh

  if [[ "$AUTO_LOAD_BUNDLES" == "true" ]]; then
    for import_file in \
      /home/user/diablo2-data/docs/tier0/postgres-bundle/import.sql \
      /home/user/diablo2-data/docs/tier0/postgres-dict-bundle/import.sql \
      /home/user/diablo2-data/docs/tier0/postgres-embedding-bundle/import.sql \
      /home/user/diablo2-data/docs/tier0/postgres-strategy-bundle/import.sql; do
      if [[ -f "$import_file" ]]; then
        echo "[entrypoint] loading bundle $import_file"
        psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -f "$import_file"
      fi
    done
  fi

  pg_ctl -D "$PGDATA" -m fast -w stop
  echo "[entrypoint] initialization complete"
fi

exec postgres -D "$PGDATA" -p "$PGPORT"
