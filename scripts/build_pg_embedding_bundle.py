#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.chroma_store import HashingEmbeddingFunction
from app.jsonl import load_jsonl

OUT_DIR = ROOT / 'docs/tier0/postgres-embedding-bundle'
DATA_DIR = OUT_DIR / 'data'
MANIFEST = OUT_DIR / 'manifest.json'
IMPORT_SQL = OUT_DIR / 'import.sql'

MERGED = ROOT / 'docs/tier0/merged'
CURATED = ROOT / 'docs/tier0/curated/chunks.jsonl'
EMBED = HashingEmbeddingFunction(dimensions=384)


def vector_literal(vector: list[float]) -> str:
    return '[' + ','.join(f'{value:.8f}' for value in vector) + ']'


def write_tsv(path: Path, rows: list[tuple[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.writer(handle, delimiter='\t', quotechar='"', lineterminator='\n')
        for row in rows:
            writer.writerow(row)


def main() -> int:
    chunks = load_jsonl(MERGED / 'chunks.jsonl')
    if CURATED.exists():
        for row in load_jsonl(CURATED):
            metadata = dict(row.get('metadata', {}))
            chunks.append({
                'chunk_id': row.get('id'),
                'text': row.get('content', ''),
                'source_id': metadata.get('source_id'),
            })
    rows: list[tuple[str, str]] = []
    texts = [str(row.get('text') or '') for row in chunks]
    vectors = EMBED.embed_documents(texts)
    for row, vector in zip(chunks, vectors):
        rows.append((str(row['chunk_id']), vector_literal(vector)))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    tsv_path = DATA_DIR / 'chunk_embeddings.tsv'
    write_tsv(tsv_path, rows)

    import_sql = f"""\\set ON_ERROR_STOP on
BEGIN;
CREATE TEMP TABLE temp_chunk_embeddings (
    chunk_id TEXT,
    embedding vector(384)
) ON COMMIT DROP;
\\copy temp_chunk_embeddings (chunk_id, embedding) FROM '{tsv_path.resolve()}' WITH (FORMAT csv, DELIMITER E'\\t', QUOTE '"')
UPDATE d2.chunks c
SET embedding = t.embedding
FROM temp_chunk_embeddings t
WHERE c.chunk_id = t.chunk_id;
COMMIT;
"""
    IMPORT_SQL.write_text(import_sql, encoding='utf-8')

    manifest = {
        'source': 'docs/tier0/merged/chunks.jsonl',
        'rows': len(rows),
        'dimensions': 384,
        'embedding_function': 'local-hashing-v1',
        'paths': {
            'chunk_embeddings': str(tsv_path.relative_to(ROOT)),
            'import_sql': str(IMPORT_SQL.relative_to(ROOT)),
        },
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'rows': len(rows), 'dimensions': 384}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
