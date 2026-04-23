\set ON_ERROR_STOP on
BEGIN;
CREATE TABLE IF NOT EXISTS d2.strategy_edge_facts (
    subject_id TEXT NOT NULL,
    predicate TEXT NOT NULL,
    object_id TEXT NOT NULL,
    priority INTEGER,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    PRIMARY KEY (subject_id, predicate, object_id)
);
TRUNCATE TABLE d2.strategy_edge_facts;
\copy d2.strategy_edge_facts (subject_id, predicate, object_id, priority, metadata) FROM '/home/user/diablo2-data/docs/tier0/postgres-strategy-bundle/data/strategy_edges.tsv' WITH (FORMAT csv, DELIMITER E'\t', QUOTE '"')
COMMIT;
