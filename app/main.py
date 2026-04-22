from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

from .service import Diablo2QAService


app = FastAPI(title="Diablo II GraphRAG Prototype")
service = Diablo2QAService()


class QARequest(BaseModel):
    query: str
    use_llm: bool = True


class AnalyzeRequest(BaseModel):
    query: str
    use_llm: bool = False


@app.get("/health")
def health() -> dict[str, object]:
    return {"ok": True, "graph_stats": service.graph.stats()}


@app.post("/ingest")
def ingest() -> dict[str, int]:
    return service.ingest()


@app.post("/analyze-query")
def analyze_query(req: AnalyzeRequest) -> dict[str, object]:
    return service.analyze_query(req.query, use_llm=req.use_llm)


@app.post("/qa")
def qa(req: QARequest) -> dict[str, object]:
    return service.answer(req.query, use_llm=req.use_llm)
