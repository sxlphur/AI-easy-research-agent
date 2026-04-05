"""
backend/extractor.py
Uses google-genai SDK directly (no OpenAI wrapper).
Model: gemini-2.5-flash — current free tier model as of 2026.
Free tier: 500 req/day, 10 RPM.

Get key: https://aistudio.google.com/app/apikey
"""

import os
import re
import json
import time
from pathlib import Path
from dotenv import load_dotenv

_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=_ENV_PATH, override=False)

MODEL = "gemini-2.5-flash"

EXTRACTION_PROMPT = """You are a research intelligence analyst. Extract structured insights from the following AI/ML research paper abstract.

Return ONLY a raw JSON object — no markdown, no backticks, no explanation.

{{
  "core_problem": "One sentence: what problem does this solve?",
  "key_idea": "One sentence: what is the central innovation?",
  "method_breakdown": ["step 1", "step 2", "step 3"],
  "results": ["result 1", "result 2"],
  "why_it_matters": "One sentence: real-world significance",
  "limitations": ["limitation 1", "limitation 2"],
  "tags": ["tag1", "tag2"],
  "relevance_score": 8.5,
  "relevance_reason": "One sentence justification"
}}

Rules:
- relevance_score MUST be a plain number 0-10, no units or fractions
- tags from: LLM, Agents, RAG, Computer Vision, NLP, Multimodal, Efficiency, Robotics, Reasoning, Fine-tuning, Benchmarks, Safety, Diffusion, Other
- Use null for missing fields

Paper Title: {title}
Abstract: {summary}
"""

_PROTECTED = {"id", "title", "authors", "link", "pdf_url", "published", "summary", "categories"}


def _get_client():
    from google import genai
    api_key = os.environ.get("GEMINI_API_KEY", "").strip().strip('"').strip("'")
    if not api_key:
        raise EnvironmentError(
            f"GEMINI_API_KEY not set. Get a free key at "
            f"https://aistudio.google.com/app/apikey and add to {_ENV_PATH}"
        )
    return genai.Client(api_key=api_key)


def _clean_json(raw: str) -> str:
    raw = raw.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.MULTILINE)
    raw = re.sub(r"\s*```$", "", raw, flags=re.MULTILINE)
    start, end = raw.find("{"), raw.rfind("}")
    if start != -1 and end != -1:
        raw = raw[start:end+1]
    return raw.strip()


def _safe_score(val) -> float:
    try:
        return max(0.0, min(10.0, float(str(val).split("/")[0].split()[0])))
    except Exception:
        return 5.0


def extract_insights(paper: dict) -> dict:
    prompt = EXTRACTION_PROMPT.format(title=paper["title"], summary=paper["summary"])

    client = _get_client()
    last_exc = None
    raw = ""

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=prompt,
            )
            raw = response.text
            break

        except EnvironmentError:
            raise

        except Exception as exc:
            last_exc = exc
            err_str = str(exc)
            if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "quota" in err_str.lower():
                m = re.search(r"retry[^\d]*(\d+)", err_str, re.IGNORECASE)
                wait = int(m.group(1)) + 3 if m else 35
                print(f"  [extractor] Rate limited — waiting {wait}s (attempt {attempt+1}/3)...")
                time.sleep(wait)
            else:
                print(f"  [extractor] Error: {type(exc).__name__}: {exc}")
                return _empty_insights(paper, f"{type(exc).__name__}: {exc}")
    else:
        print(f"  [extractor] All retries exhausted: {last_exc}")
        return _empty_insights(paper, "Rate limit exceeded after 3 retries")

    try:
        insights = json.loads(_clean_json(raw))
        insights["relevance_score"] = _safe_score(insights.get("relevance_score", 5.0))
        merged = {**insights}
        for f in _PROTECTED:
            if f in paper:
                merged[f] = paper[f]
        print(f"    ✓ score={insights['relevance_score']} tags={insights.get('tags', [])}")
        return merged

    except json.JSONDecodeError as e:
        print(f"  [extractor] JSON error: {e} | raw: {raw[:200]!r}")
        return _empty_insights(paper, f"JSON parse failed: {e}")

    except Exception as e:
        print(f"  [extractor] Unexpected: {type(e).__name__}: {e}")
        return _empty_insights(paper, f"{type(e).__name__}: {e}")


def _empty_insights(paper: dict, reason: str = "Extraction failed") -> dict:
    return {
        **paper,
        "core_problem": None, "key_idea": None,
        "method_breakdown": [], "results": [],
        "why_it_matters": None, "limitations": [],
        "tags": [], "relevance_score": 0.0,
        "relevance_reason": reason,
    }


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    sample = {
        "id": "test", "title": "Attention Is All You Need",
        "authors": ["Vaswani et al."], "link": "https://arxiv.org/abs/1706.03762",
        "pdf_url": None, "published": "2017-06-12", "categories": ["cs.CL"],
        "summary": "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks...",
    }
    print(json.dumps(extract_insights(sample), indent=2))
