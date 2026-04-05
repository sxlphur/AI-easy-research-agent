"""
api/main.py — FastAPI entry point.
Now looks for GEMINI_API_KEY instead of XAI_API_KEY.

Run from project root:
    uvicorn api.main:app --reload --port 8000
"""

import sys
import os
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_BACKEND_DIR  = _PROJECT_ROOT / "backend"

for _p in [str(_PROJECT_ROOT), str(_BACKEND_DIR)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from dotenv import load_dotenv
load_dotenv(dotenv_path=_PROJECT_ROOT / ".env", override=False)

_key = os.environ.get("GEMINI_API_KEY", "").strip().strip('"').strip("'")
if not _key:
    print("\n" + "="*60)
    print("  WARNING: GEMINI_API_KEY is not set.")
    print("  Get a free key at: https://aistudio.google.com/app/apikey")
    print(f"  Add to: {_PROJECT_ROOT / '.env'}")
    print("  Format:  GEMINI_API_KEY=AIza...  (no quotes)")
    print("="*60 + "\n")
else:
    print(f"\n  GEMINI_API_KEY loaded ({_key[:8]}...{_key[-4:]})\n")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import papers, pipeline, trends, health

app = FastAPI(
    title="AI Research Intelligence API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(papers.router,   prefix="/api/v1")
app.include_router(pipeline.router, prefix="/api/v1")
app.include_router(trends.router,   prefix="/api/v1")


@app.get("/", include_in_schema=False)
def root():
    key = os.environ.get("GEMINI_API_KEY", "")
    return {
        "service": "AI Research Intelligence API",
        "version": "1.0.0",
        "gemini_api_key_loaded": bool(key.strip()),
        "docs": "/docs",
    }
