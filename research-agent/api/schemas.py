"""
api/schemas.py
Pydantic models for all request/response contracts.
"""

from pydantic import BaseModel, Field
from typing import Optional


# ── Paper model ────────────────────────────────────────────────────────────────

class ScoreBreakdown(BaseModel):
    llm: float
    recency: float
    keyword: float


class Paper(BaseModel):
    id: str
    title: str
    authors: list[str]
    link: str
    pdf_url: Optional[str] = None
    published: str
    summary: str
    categories: list[str] = []
    fetched_date: Optional[str] = None

    # LLM extraction
    core_problem: Optional[str] = None
    key_idea: Optional[str] = None
    method_breakdown: list[str] = [] or None
    results: list[str] = [] or None
    why_it_matters: Optional[str] = None
    limitations: list[str] = [] or None 

    # Tagging & scoring
    tags: list[str] = []
    relevance_score: float = 0.0
    relevance_reason: Optional[str] = None
    final_score: float = 0.0
    score_breakdown: Optional[ScoreBreakdown] = None


# ── Request models ─────────────────────────────────────────────────────────────

class PipelineRunRequest(BaseModel):
    max_fetch: int = Field(default=15, ge=1, le=50)
    top_n: int = Field(default=10, ge=1, le=30)
    skip_seen: bool = True


class PapersQueryRequest(BaseModel):
    tags: list[str] = []
    query: str = ""
    sort_by: str = Field(default="final_score", pattern="^(final_score|published|relevance_score)$")
    limit: int = Field(default=20, ge=1, le=100)


# ── Response models ────────────────────────────────────────────────────────────

class PipelineRunResponse(BaseModel):
    success: bool
    papers_fetched: int
    papers_saved: int
    top_papers: list[Paper]
    message: str


class PapersListResponse(BaseModel):
    total: int
    papers: list[Paper]


class TrendsResponse(BaseModel):
    tag_counts: dict[str, int]
    avg_scores_by_tag: dict[str, float]
    date_counts: dict[str, int]
    total_papers: int


class StatusResponse(BaseModel):
    status: str
    total_papers: int
    latest_fetch: Optional[str]
    api_version: str = "1.0.0"
