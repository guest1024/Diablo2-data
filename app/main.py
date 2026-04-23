from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

from .service import Diablo2QAService


app = FastAPI(title="Diablo II GraphRAG Prototype")
service = Diablo2QAService()


class QARequest(BaseModel):
    query: str
    use_llm: bool = True


@app.get("/health")
def health() -> dict[str, object]:
    return {"ok": True, **service.runtime_status()}


@app.post("/ingest")
def ingest() -> dict[str, int]:
    return service.ingest()


@app.post("/qa")
def qa(req: QARequest) -> dict[str, object]:
    return service.answer(req.query, use_llm=req.use_llm)
