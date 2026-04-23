\set ON_ERROR_STOP on
BEGIN;
CREATE TEMP TABLE temp_chunk_embeddings (
    chunk_id TEXT,
    embedding vector(384)
) ON COMMIT DROP;
\copy temp_chunk_embeddings (chunk_id, embedding) FROM '/home/user/diablo2-data/crawler/artifacts/20260423T060034Z/postgres-embedding/data/chunk_embeddings.tsv' WITH (FORMAT csv, DELIMITER E'\t', QUOTE '"')
UPDATE d2.chunks AS chunks
SET embedding = temp.embedding
FROM temp_chunk_embeddings AS temp
WHERE chunks.chunk_id = temp.chunk_id;
COMMIT;
