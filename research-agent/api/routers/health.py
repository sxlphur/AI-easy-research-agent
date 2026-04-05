"""
api/routers/health.py
Health check and status endpoint.
"""

from fastapi import APIRouter
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

from utils import load_papers
from api.schemas import StatusResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=StatusResponse, summary="API health check")
def health():
    """Returns API status, total paper count, and latest fetch date."""
    papers = load_papers()
    dates = [p.get("fetched_date") for p in papers if p.get("fetched_date")]
    latest = max(dates) if dates else None

    return StatusResponse(
        status="ok",
        total_papers=len(papers),
        latest_fetch=latest,
    )
