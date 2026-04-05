"""
fetch_papers.py
Fetches the latest AI/ML research papers from arXiv.
"""

import arxiv
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path

CATEGORIES = ["cs.AI", "cs.LG", "cs.CL", "cs.CV"]
MAX_RESULTS = 20
DATA_FILE = Path(__file__).parent.parent / "data" / "papers.json"
SEEN_FILE = Path(__file__).parent.parent / "data" / "seen.json"


def _paper_id(paper) -> str:
    return hashlib.md5(paper.title.encode()).hexdigest()


def load_seen_ids() -> set:
    if SEEN_FILE.exists():
        with open(SEEN_FILE) as f:
            return set(json.load(f))
    return set()


def save_seen_ids(seen: set):
    SEEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)


def fetch_papers(max_results: int = MAX_RESULTS, skip_seen: bool = True) -> list[dict]:
    """
    Fetches recent papers from arXiv across AI/ML categories.
    Returns a list of raw paper dicts.
    """
    seen_ids = load_seen_ids() if skip_seen else set()
    query = " OR ".join(f"cat:{cat}" for cat in CATEGORIES)

    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending,
    )

    papers = []
    new_seen = set(seen_ids)

    for result in search.results():
        pid = _paper_id(result)
        if skip_seen and pid in seen_ids:
            continue

        papers.append({
            "id": pid,
            "title": result.title,
            "authors": [str(a) for a in result.authors],
            "link": result.entry_id,
            "pdf_url": result.pdf_url,
            "published": result.published.strftime("%Y-%m-%d"),
            "summary": result.summary,
            "categories": result.categories,
        })
        new_seen.add(pid)

    save_seen_ids(new_seen)
    return papers


if __name__ == "__main__":
    papers = fetch_papers()
    print(f"Fetched {len(papers)} new papers.")
    for p in papers[:3]:
        print(f"  - {p['title'][:80]}")
