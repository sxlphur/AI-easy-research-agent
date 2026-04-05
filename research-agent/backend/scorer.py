"""
scorer.py — relevance scoring with robust type handling.

FIX: relevance_score from Gemini can come back as a string ("8.5"),
     a string with suffix ("8.5/10"), or null. All cases handled safely.
"""

from datetime import datetime

HIGH_VALUE_KEYWORDS = [
    "agent", "reasoning", "efficient", "multimodal", "llm",
    "rag", "alignment", "safety", "real-world", "benchmark",
    "tool use", "planning", "scaling"
]


def _safe_float(value, default: float = 5.0) -> float:
    """Convert anything Gemini might return to a float."""
    if value is None:
        return default
    try:
        # Handle "8.5/10", "8.5 / 10", "8.5 out of 10"
        s = str(value).strip().split("/")[0].split()[0]
        result = float(s)
        # Clamp to 0-10
        return max(0.0, min(10.0, result))
    except (ValueError, IndexError):
        return default


def recency_score(published_date: str) -> float:
    try:
        pub = datetime.strptime(published_date, "%Y-%m-%d")
        age_days = (datetime.utcnow() - pub).days
        if age_days <= 1:   return 10.0
        elif age_days <= 3: return 9.0
        elif age_days <= 7: return 7.5
        elif age_days <= 14: return 5.0
        else: return 2.0
    except Exception:
        return 5.0


def keyword_score(paper: dict) -> float:
    text = f"{paper.get('title', '')} {paper.get('summary', '')}".lower()
    hits = sum(1 for kw in HIGH_VALUE_KEYWORDS if kw in text)
    return min(hits * 1.5, 10.0)


def compute_final_score(paper: dict) -> dict:
    llm_score = _safe_float(paper.get("relevance_score"), default=5.0)
    rec = recency_score(paper.get("published", ""))
    kw = keyword_score(paper)

    final = (0.40 * llm_score) + (0.35 * rec) + (0.25 * kw)
    paper["final_score"] = round(final, 2)
    paper["score_breakdown"] = {
        "llm": round(llm_score, 2),
        "recency": round(rec, 2),
        "keyword": round(kw, 2),
    }
    return paper


def rank_papers(papers: list[dict], top_n: int = 5) -> list[dict]:
    scored = [compute_final_score(p) for p in papers]
    scored.sort(key=lambda x: x["final_score"], reverse=True)
    return scored[:top_n]
