-- Optional: only run this file when pgvector is installed in your PostgreSQL instance.
CREATE EXTENSION IF NOT EXISTS vector;

ALTER TABLE d2.chunks
    ADD COLUMN IF NOT EXISTS embedding VECTOR(384);

CREATE INDEX IF NOT EXISTS d2_chunks_embedding_ivfflat_idx
    ON d2.chunks USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);
