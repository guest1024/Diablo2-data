\set ON_ERROR_STOP on
BEGIN;
CREATE TEMP TABLE temp_documents (
    doc_id TEXT,
    source_id TEXT,
    source_name TEXT,
    label TEXT,
    source_url TEXT,
    local_path TEXT,
    content_type TEXT,
    authority_tier TEXT,
    lane TEXT,
    title TEXT,
    text_content TEXT,
    char_count INTEGER,
    metadata JSONB
) ON COMMIT DROP;
CREATE TEMP TABLE temp_chunks (
    chunk_id TEXT,
    doc_id TEXT,
    source_id TEXT,
    source_name TEXT,
    source_url TEXT,
    label TEXT,
    title TEXT,
    lane TEXT,
    authority_tier TEXT,
    chunk_index INTEGER,
    text_content TEXT,
    char_count INTEGER,
    metadata JSONB
) ON COMMIT DROP;
\copy temp_documents (doc_id, source_id, source_name, label, source_url, local_path, content_type, authority_tier, lane, title, text_content, char_count, metadata) FROM '/home/user/diablo2-data/crawler/artifacts/20260423T060034Z/postgres/data/documents.tsv' WITH (FORMAT csv, DELIMITER E'\t', QUOTE '"')
\copy temp_chunks (chunk_id, doc_id, source_id, source_name, source_url, label, title, lane, authority_tier, chunk_index, text_content, char_count, metadata) FROM '/home/user/diablo2-data/crawler/artifacts/20260423T060034Z/postgres/data/chunks.tsv' WITH (FORMAT csv, DELIMITER E'\t', QUOTE '"')
INSERT INTO d2.documents (doc_id, source_id, source_name, label, source_url, local_path, content_type, authority_tier, lane, title, text_content, char_count, metadata)
SELECT doc_id, source_id, source_name, label, source_url, local_path, content_type, authority_tier, lane, title, text_content, char_count, metadata FROM temp_documents
ON CONFLICT (doc_id) DO UPDATE SET
    title = EXCLUDED.title,
    text_content = EXCLUDED.text_content,
    char_count = EXCLUDED.char_count,
    metadata = EXCLUDED.metadata;
INSERT INTO d2.chunks (chunk_id, doc_id, source_id, source_name, source_url, label, title, lane, authority_tier, chunk_index, text_content, char_count, metadata)
SELECT chunk_id, doc_id, source_id, source_name, source_url, label, title, lane, authority_tier, chunk_index, text_content, char_count, metadata FROM temp_chunks
ON CONFLICT (chunk_id) DO UPDATE SET
    text_content = EXCLUDED.text_content,
    char_count = EXCLUDED.char_count,
    metadata = EXCLUDED.metadata;
COMMIT;
