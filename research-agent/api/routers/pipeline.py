"""
api/routers/pipeline.py
"""

import sys
import traceback
from pathlib import Path

_BACKEND = Path(__file__).resolve().parent.parent.parent / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from fastapi import APIRouter, HTTPException
from api.schemas import PipelineRunRequest, PipelineRunResponse, Paper

router = APIRouter(prefix="/pipeline", tags=["Pipeline"])
_pipeline_running = False


def _to_paper(p: dict) -> Paper:
    """
    Safely convert a raw paper dict to a Paper schema object.
    Handles the score_breakdown dict → ScoreBreakdown coercion explicitly,
    and drops any other unexpected fields via extra='ignore'.
    """
    from api.schemas import ScoreBreakdown

    # Coerce score_breakdown dict → ScoreBreakdown if needed
    sb = p.get("score_breakdown")
    if isinstance(sb, dict):
        p = {**p, "score_breakdown": ScoreBreakdown(**sb)}

    # Ensure relevance_score is always a float
    try:
        p = {**p, "relevance_score": float(str(p.get("relevance_score", 0.0)).split("/")[0].split()[0])}
    except Exception:
        p = {**p, "relevance_score": 0.0}

    return Paper(**p)


@router.post("/run", response_model=PipelineRunResponse)
def run_pipeline_endpoint(body: PipelineRunRequest):
    global _pipeline_running
    if _pipeline_running:
        raise HTTPException(status_code=409, detail="Pipeline already running.")

    _pipeline_running = True
    try:
        from pipeline import run_pipeline as _run
        papers = _run(
            max_fetch=body.max_fetch,
            top_n=body.top_n,
            skip_seen=body.skip_seen,
            verbose=True,
        )

        safe_papers = []
        for p in papers:
            try:
                safe_papers.append(_to_paper(p))
            except Exception as e:
                print(f"[router] Schema conversion failed for '{p.get('title','?')[:50]}': {e}")
                traceback.print_exc()

        print(f"[router] Returning {len(safe_papers)}/{len(papers)} papers in response")

        return PipelineRunResponse(
            success=True,
            papers_fetched=body.max_fetch,
            papers_saved=len(safe_papers),
            top_papers=safe_papers,
            message=f"Pipeline complete. {len(safe_papers)} papers ready.",
        )

    except EnvironmentError as e:
        raise HTTPException(status_code=400, detail=f"Missing API key: {e}")

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {e}")

    finally:
        _pipeline_running = False


@router.get("/status")
def pipeline_status():
    return {"running": _pipeline_running}


@router.get("/debug", summary="Verify key, imports, and a live API call")
def debug():
    import os
    report = {}

    key = os.environ.get("GEMINI_API_KEY", "").strip()
    report["GEMINI_API_KEY_set"] = bool(key)
    report["GEMINI_API_KEY_preview"] = f"{key[:8]}...{key[-4:]}" if len(key) > 12 else "MISSING"

    for mod in ["fetch_papers", "extractor", "tagger", "scorer", "pipeline", "utils"]:
        try:
            __import__(mod)
            report[f"import_{mod}"] = "ok"
        except Exception as e:
            report[f"import_{mod}"] = f"FAILED: {e}"

    try:
        from google import genai
        client = genai.Client(api_key=key)
        resp = client.models.generate_content(
            model="gemini-2.5-flash",
            contents='Reply with only the word: working',
        )
        report["gemini_api_call"] = resp.text.strip()
    except Exception as e:
        report["gemini_api_call"] = f"FAILED: {type(e).__name__}: {e}"

    return report
