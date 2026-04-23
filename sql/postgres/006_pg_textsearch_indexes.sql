-- PostgreSQL 17/18 BM25 index recommendations for pg_textsearch runtime.
-- Requires:
--   shared_preload_libraries = 'pg_textsearch'
--   CREATE EXTENSION pg_textsearch;

-- Main lexical index for chunk body.
CREATE INDEX IF NOT EXISTS d2_chunks_bm25_text_idx
    ON d2.chunks
    USING bm25 (text_content)
    WITH (text_config = 'english');

-- Title-focused index to boost short exact entity/title lookups.
CREATE INDEX IF NOT EXISTS d2_chunks_bm25_title_idx
    ON d2.chunks
    USING bm25 (title)
    WITH (text_config = 'english');

-- Optional multilingual / pre-tokenized lane.
-- If later you materialize lexical_text_mixed or lexical_text_zh columns,
-- create dedicated BM25 indexes there instead of overloading raw text_content.
