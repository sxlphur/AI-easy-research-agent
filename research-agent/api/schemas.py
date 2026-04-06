from pydantic import BaseModel, Field
from typing import Optional

LIST_FIELDS = ["method_breakdown", "results", "limitations", "tags", "authors", "categories"]

def sanitize_paper(p: dict) -> dict:
    """Call this BEFORE Paper(**p). Coerces None lists and bad score types."""
    p = dict(p)
    for f in LIST_FIELDS:
        if not isinstance(p.get(f), list):
            p[f] = []
    try:
        p["relevance_score"] = float(str(p.get("relevance_score", 0)).split("/")[0].split()[0])
    except Exception:
        p["relevance_score"] = 0.0
    sb = p.get("score_breakdown")
    if isinstance(sb, dict):
        p["score_breakdown"] = ScoreBreakdown(**sb)
    return p

class ScoreBreakdown(BaseModel):
    model_config = {"extra": "ignore"}
    llm: float = 0.0
    recency: float = 0.0
    keyword: float = 0.0

class Paper(BaseModel):
    model_config = {"extra": "ignore"}
    id: str
    title: str
    authors: list[str] = []
    link: str = ""
    pdf_url: Optional[str] = None
    published: str = ""
    summary: str = ""
    categories: list[str] = []
    fetched_date: Optional[str] = None
    core_problem: Optional[str] = None
    key_idea: Optional[str] = None
    method_breakdown: list[str] = []
    results: list[str] = []
    why_it_matters: Optional[str] = None
    limitations: list[str] = []
    tags: list[str] = []
    relevance_score: float = 0.0
    relevance_reason: Optional[str] = None
    final_score: float = 0.0
    score_breakdown: Optional[ScoreBreakdown] = None

class PipelineRunRequest(BaseModel):
    max_fetch: int = Field(default=15, ge=1, le=50)
    top_n: int = Field(default=10, ge=1, le=30)
    skip_seen: bool = True

class PapersQueryRequest(BaseModel):
    tags: list[str] = []
    query: str = ""
    sort_by: str = Field(default="final_score", pattern="^(final_score|published|relevance_score)$")
    limit: int = Field(default=20, ge=1, le=100)

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
    latest_fetch: Optional[str] = None
    api_version: str = "1.0.0"
