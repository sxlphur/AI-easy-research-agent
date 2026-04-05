"""
backend/utils.py — Storage, filtering, deduplication.
"""

import json
from pathlib import Path
from datetime import datetime

DATA_DIR   = Path(__file__).resolve().parent.parent / "data"
PAPERS_FILE = DATA_DIR / "papers.json"


def ensure_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_papers() -> list[dict]:
    ensure_data_dir()
    if PAPERS_FILE.exists():
        try:
            with open(PAPERS_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def save_papers(papers: list[dict]) -> int:
    """
    Merge new papers into the store. Returns count of truly new ones.
    Always writes so the file is up to date even if all papers existed.
    """
    ensure_data_dir()
    existing   = load_papers()
    existing_ids = {p["id"] for p in existing if "id" in p}

    new_papers = [p for p in papers if p.get("id") not in existing_ids]
    all_papers = new_papers + existing
    all_papers = all_papers[:200]

    with open(PAPERS_FILE, "w") as f:
        json.dump(all_papers, f, indent=2, default=str)

    # Return total saved (even if 0 new, file was still written)
    print(f"  [utils] {len(new_papers)} new + {len(existing)} existing = {len(all_papers)} total stored")
    return len(new_papers)


def filter_by_tags(papers: list[dict], tags: list[str]) -> list[dict]:
    if not tags:
        return papers
    tags_lower = [t.lower() for t in tags]
    return [p for p in papers if any(t.lower() in tags_lower for t in p.get("tags", []))]


def filter_by_query(papers: list[dict], query: str) -> list[dict]:
    if not query.strip():
        return papers
    keywords = query.lower().split()
    def matches(p):
        text = f"{p.get('title','')} {p.get('summary','')} {p.get('why_it_matters','')}".lower()
        return any(kw in text for kw in keywords)
    return [p for p in papers if matches(p)]



