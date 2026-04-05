"""
pipeline.py
Main orchestration: fetch → extract → tag → score → store
"""

import sys
import os
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from fetch_papers import fetch_papers
from extractor import extract_insights
from tagger import tag_paper
from scorer import rank_papers
from utils import save_papers


def run_pipeline(
    max_fetch: int = 20,
    top_n: int = 10,
    skip_seen: bool = True,
    verbose: bool = True,
) -> list[dict]:
    """
    Full pipeline run.
    Returns the top-ranked, enriched papers.
    """
    if verbose:
        print(f"\n🔍 [{datetime.utcnow().strftime('%Y-%m-%d %H:%M')}] Starting pipeline...")

    # Step 1: Fetch
    papers = fetch_papers(max_results=max_fetch, skip_seen=skip_seen)
    if verbose:
        print(f"  ✅ Fetched {len(papers)} new papers from arXiv")

    if not papers:
        if verbose:
            print("  ℹ️  No new papers found. Try running with skip_seen=False.")
        return []

    # Step 2: Extract insights (LLM)
    enriched = []
    for i, paper in enumerate(papers):
        if verbose:
            print(f"  🧠 Extracting [{i+1}/{len(papers)}]: {paper['title'][:60]}...")
        enriched_paper = extract_insights(paper)
        enriched.append(enriched_paper)

    # Step 3: Tag
    tagged = [tag_paper(p) for p in enriched]

    # Step 4: Score & rank
    ranked = rank_papers(tagged, top_n=top_n)

    # Step 5: Add fetch metadata
    today = datetime.utcnow().strftime("%Y-%m-%d")
    for p in ranked:
        p["fetched_date"] = today

    # Step 6: Store
    saved = save_papers(ranked)
    if verbose:
        print(f"  💾 Saved {saved} new papers to data/papers.json")
        print(f"\n🏆 Top {len(ranked)} papers ranked and ready!\n")
        for i, p in enumerate(ranked, 1):
            print(f"  {i}. [{p.get('final_score', 0):.1f}] {p['title'][:70]}")

    return ranked


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run the AI Research Intelligence Pipeline")
    parser.add_argument("--max", type=int, default=20, help="Max papers to fetch")
    parser.add_argument("--top", type=int, default=10, help="Top N to keep")
    parser.add_argument("--fresh", action="store_true", help="Skip deduplication (refetch all)")
    args = parser.parse_args()

    run_pipeline(max_fetch=args.max, top_n=args.top, skip_seen=not args.fresh)
