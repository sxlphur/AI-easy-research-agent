import sys
from pathlib import Path

_BACKEND = Path(__file__).resolve().parent.parent.parent / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from utils import load_papers, filter_by_tags, filter_by_query
from api.schemas import Paper, PapersListResponse, PapersQueryRequest, sanitize_paper

router = APIRouter(prefix="/papers", tags=["Papers"])

def _sort(papers, sort_by):
    key = {"final_score": lambda p: p.get("final_score",0),
           "published":   lambda p: p.get("published",""),
           "relevance_score": lambda p: p.get("relevance_score",0)}.get(sort_by, lambda p: p.get("final_score",0))
    return sorted(papers, key=key, reverse=True)

def _safe_papers(raw_list):
    out = []
    for p in raw_list:
        try:
            out.append(Paper(**sanitize_paper(p)))
        except Exception as e:
            print(f"[papers] skipping '{p.get('title','')[:50]}': {e}")
    return out

@router.get("/", response_model=PapersListResponse)
def list_papers(
    tags: Optional[str] = Query(None),
    query: Optional[str] = Query(None),
    sort_by: str = Query("final_score"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    papers = load_papers()
    if tags:
        papers = filter_by_tags(papers, [t.strip() for t in tags.split(",")])
    if query:
        papers = filter_by_query(papers, query)
    papers = _sort(papers, sort_by)
    total = len(papers)
    return PapersListResponse(total=total, papers=_safe_papers(papers[offset:offset+limit]))

@router.post("/search", response_model=PapersListResponse)
def search_papers(body: PapersQueryRequest):
    papers = load_papers()
    if body.tags:
        papers = filter_by_tags(papers, body.tags)
    if body.query:
        papers = filter_by_query(papers, body.query)
    papers = _sort(papers, body.sort_by)[:body.limit]
    return PapersListResponse(total=len(papers), papers=_safe_papers(papers))

@router.get("/{paper_id}", response_model=Paper)
def get_paper(paper_id: str):
    for p in load_papers():
        if p.get("id") == paper_id:
            return Paper(**sanitize_paper(p))
    raise HTTPException(status_code=404, detail="Paper not found.")
