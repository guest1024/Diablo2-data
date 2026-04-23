\set ON_ERROR_STOP on
BEGIN;
CREATE TEMP TABLE temp_chunk_embeddings (
    chunk_id TEXT,
    embedding vector(384)
) ON COMMIT DROP;
\copy temp_chunk_embeddings (chunk_id, embedding) FROM '/home/user/diablo2-data/docs/tier0/postgres-embedding-bundle/data/chunk_embeddings.tsv' WITH (FORMAT csv, DELIMITER E'\t', QUOTE '"')
UPDATE d2.chunks c
SET embedding = t.embedding
FROM temp_chunk_embeddings t
WHERE c.chunk_id = t.chunk_id;
COMMIT;
