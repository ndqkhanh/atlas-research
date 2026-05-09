"""FastAPI HTTP surface for Atlas-Research."""
from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field

from .models import Brief
from .pipeline import AtlasPipeline

app = FastAPI(
    title="Atlas-Research",
    description="Long-horizon research agent with planner + retrieval + citation verifier.",
    version="0.1.0",
)

_pipeline = AtlasPipeline()


class ReportRequest(BaseModel):
    question: str = Field(..., description="Research question.")
    audience: str = Field(default="technical")
    style: str = Field(default="standard")
    max_cost_usd: float = Field(default=3.0, ge=0.1, le=100.0)
    target_length_words: int = Field(default=2500, ge=200, le=10000)


class ReportResponse(BaseModel):
    markdown: str
    faithfulness_ratio: float
    total_claims: int
    verified_claims: int
    cost_usd: float


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok", "service": "atlas-research"}


@app.post("/v1/reports", response_model=ReportResponse)
def create_report(req: ReportRequest) -> ReportResponse:
    brief = Brief(
        question=req.question,
        audience=req.audience,
        style=req.style,
        max_cost_usd=req.max_cost_usd,
        target_length_words=req.target_length_words,
    )
    result = _pipeline.run(brief)
    return ReportResponse(
        markdown=result.report.to_markdown(),
        faithfulness_ratio=result.report.faithfulness_ratio,
        total_claims=result.verification.total_claims,
        verified_claims=result.verification.verified_claims,
        cost_usd=result.report.cost_usd,
    )
