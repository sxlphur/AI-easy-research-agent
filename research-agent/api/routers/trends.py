"""
api/routers/trends.py
Analytics endpoints: tag distribution, score averages, date timeline.
"""

from fastapi import APIRouter
from collections import Counter
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

from utils import load_papers
from api.schemas import TrendsResponse

router = APIRouter(prefix="/trends", tags=["Trends"])


@router.get("/", response_model=TrendsResponse, summary="Get research trend analytics")
def get_trends():
    """
    Returns aggregated analytics across all stored papers:
    - Tag frequency counts
    - Average relevance score per tag
    - Papers published per date
    """
    papers = load_papers()

    tag_counts = Counter(t for p in papers for t in p.get("tags", []))

    avg_scores: dict[str, float] = {}
    tag_paper_map: dict[str, list[float]] = {}
    for p in papers:
        for t in p.get("tags", []):
            tag_paper_map.setdefault(t, []).append(p.get("final_score", 0))
    for tag, scores in tag_paper_map.items():
        avg_scores[tag] = round(sum(scores) / len(scores), 2)

    date_counts = Counter(p.get("published", "unknown") for p in papers)

    return TrendsResponse(
        tag_counts=dict(tag_counts.most_common()),
        avg_scores_by_tag=avg_scores,
        date_counts=dict(sorted(date_counts.items(), reverse=True)),
        total_papers=len(papers),
    )


@router.get("/tags", summary="List all known tags with counts")
def list_tags():
    """Quick endpoint: returns just tag → count mapping, sorted by frequency."""
    papers = load_papers()
    counts = Counter(t for p in papers for t in p.get("tags", []))
    return {"tags": dict(counts.most_common())}
