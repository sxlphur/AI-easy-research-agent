"""
api/routers/papers.py
Endpoints for fetching, filtering, and reading papers.
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

from utils import load_papers, filter_by_tags, filter_by_query
from api.schemas import Paper, PapersListResponse, PapersQueryRequest

router = APIRouter(prefix="/papers", tags=["Papers"])


def _sort_papers(papers: list[dict], sort_by: str) -> list[dict]:
    key_map = {
        "final_score":      lambda p: p.get("final_score", 0),
        "published":        lambda p: p.get("published", ""),
        "relevance_score":  lambda p: p.get("relevance_score", 0),
    }
    return sorted(papers, key=key_map.get(sort_by, key_map["final_score"]), reverse=True)


@router.get("/", response_model=PapersListResponse, summary="List all stored papers")
def list_papers(
    tags: Optional[str] = Query(None, description="Comma-separated tags, e.g. LLM,Agents"),
    query: Optional[str] = Query(None, description="Free-text keyword search"),
    sort_by: str = Query("final_score", pattern="^(final_score|published|relevance_score)$"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """
    Return stored papers with optional filtering by tags and keyword search.
    Supports sorting by final_score, published date, or raw relevance_score.
    """
    papers = load_papers()

    if tags:
        tag_list = [t.strip() for t in tags.split(",") if t.strip()]
        papers = filter_by_tags(papers, tag_list)

    if query:
        papers = filter_by_query(papers, query)

    papers = _sort_papers(papers, sort_by)
    total = len(papers)
    papers = papers[offset: offset + limit]

    return PapersListResponse(total=total, papers=[Paper(**p) for p in papers])


@router.post("/search", response_model=PapersListResponse, summary="Advanced paper search")
def search_papers(body: PapersQueryRequest):
    """
    Advanced search — accepts a JSON body with tags, query string, sort preference, and limit.
    """
    papers = load_papers()

    if body.tags:
        papers = filter_by_tags(papers, body.tags)
    if body.query:
        papers = filter_by_query(papers, body.query)

    papers = _sort_papers(papers, body.sort_by)
    papers = papers[: body.limit]

    return PapersListResponse(total=len(papers), papers=[Paper(**p) for p in papers])


@router.get("/{paper_id}", response_model=Paper, summary="Get a single paper by ID")
def get_paper(paper_id: str):
    """Return a single paper by its MD5 ID."""
    papers = load_papers()
    for p in papers:
        if p.get("id") == paper_id:
            return Paper(**p)
    raise HTTPException(status_code=404, detail=f"Paper '{paper_id}' not found.")
