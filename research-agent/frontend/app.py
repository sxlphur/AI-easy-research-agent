"""
frontend/app.py
Streamlit UI — communicates ONLY via the FastAPI backend.
No direct backend imports anywhere in this file.

Start the API first:
    uvicorn api.main:app --reload --port 8000

Then start this:
    streamlit run frontend/app.py
"""

import streamlit as st
import requests
from datetime import datetime

# ── Config ─────────────────────────────────────────────────────────────────────
API_BASE = "http://localhost:8000/api/v1"
HEALTH_URL = "http://localhost:8000/health"

PALETTE = {
    "cafe_noir":   "#4C3D19",
    "kombu_green": "#354024",
    "moss_green":  "#889063",
    "tan":         "#CFBB99",
    "bone":        "#E5D7C4",
}

# ── API client helpers ─────────────────────────────────────────────────────────

def api_get(path: str, params: dict = None) -> dict | None:
    try:
        r = requests.get(f"{API_BASE}{path}", params=params, timeout=30)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        st.error("Cannot reach the API. Run: `uvicorn api.main:app --reload --port 8000`")
        return None
    except Exception as e:
        st.error(f"API error: {e}")
        return None


def api_post(path: str, body: dict = None) -> dict | None:
    try:
        r = requests.post(f"{API_BASE}{path}", json=body or {}, timeout=120)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        st.error("Cannot reach the API. Run: `uvicorn api.main:app --reload --port 8000`")
        return None
    except Exception as e:
        st.error(f"API error: {e}")
        return None


def api_health() -> dict | None:
    try:
        r = requests.get(HEALTH_URL, timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Arxiv Intelligence",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,400&family=DM+Sans:wght@300;400;500&family=DM+Mono:wght@400;500&display=swap');

  html, body, [class*="css"] {{
    font-family: 'DM Sans', sans-serif;
    background-color: {PALETTE['bone']};
    color: {PALETTE['cafe_noir']};
  }}
  .stApp {{ background-color: {PALETTE['bone']}; }}

  [data-testid="stSidebar"] {{ background-color: {PALETTE['kombu_green']} !important; }}
  [data-testid="stSidebar"] * {{ color: {PALETTE['bone']} !important; }}
  [data-testid="stSidebar"] label {{
    color: {PALETTE['bone']} !important; font-size: 0.8rem; font-weight: 500;
    letter-spacing: 0.06em; text-transform: uppercase;
  }}
  [data-testid="stSidebar"] .stButton button {{
    background-color: {PALETTE['moss_green']} !important; color: {PALETTE['bone']} !important;
    border: none; border-radius: 4px; font-weight: 500; letter-spacing: 0.05em;
    text-transform: uppercase; font-size: 0.78rem; width: 100%; padding: 0.6rem 1rem;
  }}
  [data-testid="stSidebar"] .stButton button:hover {{ background-color: {PALETTE['cafe_noir']} !important; }}
  [data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] {{
    background-color: {PALETTE['moss_green']} !important; color: #fff !important; border-radius: 3px;
  }}

  .main-header {{
    padding: 2rem 0 1rem; border-bottom: 2px solid {PALETTE['moss_green']}; margin-bottom: 1.5rem;
  }}
  .main-header h1 {{
    font-family: 'Playfair Display', serif; font-size: 2.4rem;
    color: {PALETTE['kombu_green']}; margin: 0; line-height: 1.1;
  }}
  .main-header .subtitle {{
    font-size: 0.72rem; color: {PALETTE['moss_green']};
    letter-spacing: 0.12em; text-transform: uppercase; margin-top: 4px;
  }}
  .api-badge {{
    display: inline-block; font-family: 'DM Mono', monospace;
    font-size: 0.65rem; padding: 2px 8px; border-radius: 3px;
    margin-left: 0.7rem; vertical-align: middle;
  }}
  .api-ok   {{ background: {PALETTE['moss_green']}25; color: {PALETTE['kombu_green']}; border: 1px solid {PALETTE['moss_green']}55; }}
  .api-down {{ background: #c0392b18; color: #c0392b; border: 1px solid #c0392b45; }}

  .stats-bar {{ display: flex; gap: 0.8rem; margin-bottom: 1.5rem; flex-wrap: wrap; }}
  .chip {{ background: {PALETTE['tan']}; border: 1px solid {PALETTE['moss_green']}40;
           border-radius: 4px; padding: 3px 10px; font-size: 0.72rem; font-weight: 500; color: {PALETTE['kombu_green']}; }}

  .paper-card {{
    background: white; border-radius: 8px; padding: 1.4rem 1.6rem;
    margin-bottom: 1rem; border-left: 5px solid {PALETTE['moss_green']};
    box-shadow: 0 2px 10px {PALETTE['cafe_noir']}12; position: relative;
    transition: box-shadow 0.2s, transform 0.2s;
  }}
  .paper-card:hover {{ box-shadow: 0 5px 20px {PALETTE['cafe_noir']}20; transform: translateY(-1px); }}
  .paper-card.top   {{ border-left-color: {PALETTE['cafe_noir']}; }}

  .score-badge {{
    position: absolute; top: 1rem; right: 1.2rem; font-family: 'DM Mono', monospace;
    font-size: 0.82rem; font-weight: 500; padding: 3px 9px; border-radius: 4px; line-height: 1;
    background: {PALETTE['kombu_green']}; color: {PALETTE['bone']};
  }}
  .score-badge.hi  {{ background: {PALETTE['cafe_noir']}; }}
  .score-badge.mid {{ background: {PALETTE['moss_green']}; color: #fff; }}

  .card-title {{
    font-family: 'Playfair Display', serif; font-size: 1.05rem; color: {PALETTE['kombu_green']};
    font-weight: 700; margin: 0 3.5rem 0.2rem 0; line-height: 1.35;
  }}
  .card-meta {{ font-size: 0.7rem; color: {PALETTE['moss_green']}; margin-bottom: 0.6rem; }}

  .ctag {{
    display: inline-block; background: {PALETTE['bone']}; border: 1px solid {PALETTE['moss_green']};
    color: {PALETTE['kombu_green']}; border-radius: 3px; padding: 2px 7px;
    font-size: 0.62rem; font-weight: 500; letter-spacing: 0.05em; text-transform: uppercase;
    margin: 0 3px 3px 0;
  }}

  .why-matters {{
    background: {PALETTE['bone']}; border-left: 3px solid {PALETTE['moss_green']}; border-radius: 0;
    padding: 8px 12px; margin: 0.7rem 0; font-size: 0.83rem; color: {PALETTE['kombu_green']};
    font-style: italic; line-height: 1.5; font-family: 'Playfair Display', serif;
  }}
  .sec-label {{
    font-size: 0.62rem; font-weight: 500; letter-spacing: 0.1em; text-transform: uppercase;
    color: {PALETTE['moss_green']}; display: block; margin-bottom: 3px;
  }}
  .sec-body {{ font-size: 0.82rem; color: {PALETTE['cafe_noir']}; line-height: 1.65; }}
  .sec-body ul {{ padding-left: 1.1rem; margin: 0; }}
  .sec-body li {{ margin-bottom: 2px; }}
  .card-link {{
    font-size: 0.74rem; color: {PALETTE['moss_green']}; text-decoration: none;
    border-bottom: 1px solid {PALETTE['moss_green']}50; margin-top: 0.6rem; display: inline-block;
  }}

  .empty-state {{ text-align: center; padding: 4rem 2rem; color: {PALETTE['moss_green']}; }}
  .empty-state h3 {{ font-family: 'Playfair Display', serif; font-size: 1.6rem; color: {PALETTE['kombu_green']}; margin-bottom: 0.5rem; }}

  .trend-row {{ display: flex; align-items: center; gap: 10px; margin-bottom: 6px; }}
  .trend-name {{ font-size: 0.78rem; color: {PALETTE['kombu_green']}; font-weight: 500; width: 110px; flex-shrink: 0; }}
  .trend-bg {{ flex: 1; background: {PALETTE['moss_green']}30; border-radius: 2px; height: 8px; }}
  .trend-fill {{ height: 8px; border-radius: 2px; background: {PALETTE['moss_green']}; }}
  .trend-val {{ font-size: 0.7rem; color: {PALETTE['moss_green']}; font-family: 'DM Mono', monospace; width: 24px; text-align: right; }}

  .stTabs [data-baseweb="tab"] {{
    background-color: {PALETTE['tan']}80; border-radius: 4px 4px 0 0;
    color: {PALETTE['kombu_green']}; font-size: 0.78rem; font-weight: 500;
    letter-spacing: 0.06em; text-transform: uppercase;
    padding: 0.45rem 1.1rem; border: none; font-family: 'DM Sans', sans-serif;
  }}
  .stTabs [aria-selected="true"] {{ background-color: {PALETTE['kombu_green']} !important; color: {PALETTE['bone']} !important; }}
  .stTabs [data-baseweb="tab-list"] {{ background: transparent; gap: 4px; }}

  .stButton > button {{
    background-color: {PALETTE['kombu_green']}; color: {PALETTE['bone']};
    border: none; border-radius: 5px; font-weight: 500; letter-spacing: 0.05em;
    text-transform: uppercase; font-size: 0.78rem; padding: 0.55rem 1.4rem;
    font-family: 'DM Sans', sans-serif;
  }}
  .stButton > button:hover {{ background-color: {PALETTE['cafe_noir']}; }}

  .endpoint-box {{
    background: white; border-radius: 6px; padding: 0.9rem 1.1rem;
    border: 1px solid {PALETTE['moss_green']}35; margin-bottom: 0.5rem;
  }}
  .ep-method {{ font-family: 'DM Mono', monospace; font-size: 0.7rem; font-weight: 500; padding: 2px 7px; border-radius: 3px; margin-right: 8px; }}
  .ep-get    {{ background: #1d9e7520; color: #0f6e56; }}
  .ep-post   {{ background: #378add20; color: #185fa5; }}
  .ep-path   {{ font-family: 'DM Mono', monospace; font-size: 0.8rem; color: {PALETTE['kombu_green']}; }}
  .ep-desc   {{ font-size: 0.76rem; color: {PALETTE['moss_green']}; margin-top: 3px; }}
</style>
""", unsafe_allow_html=True)


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌿 Arxiv Intelligence")
    st.markdown("---")

    st.markdown("### Filter by Topic")
    ALL_TAGS = ["LLM","Agents","RAG","Computer Vision","NLP","Multimodal",
                "Efficiency","Robotics","Reasoning","Fine-tuning","Benchmarks","Safety","Diffusion"]
    selected_tags = st.multiselect("Topics", options=ALL_TAGS, default=[], label_visibility="collapsed")

    st.markdown("### Custom Search")
    custom_query = st.text_input("Search", placeholder="e.g. efficient small models", label_visibility="collapsed")

    st.markdown("### Sort By")
    sort_by = st.radio(
        "Sort",
        options=["final_score", "published", "relevance_score"],
        format_func=lambda x: {"final_score":"Final Score","published":"Recency","relevance_score":"LLM Score"}[x],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown("### Run Pipeline")
    max_fetch = st.slider("Papers to fetch", 5, 30, 15)
    top_n     = st.slider("Top N to keep", 3, 15, 8)
    skip_seen = st.checkbox("Skip seen papers", value=True)

    if st.button("🔄 Fetch & Analyze"):
        with st.spinner("Calling POST /api/v1/pipeline/run ..."):
            result = api_post("/pipeline/run", {"max_fetch": max_fetch, "top_n": top_n, "skip_seen": skip_seen})
            if result:
                st.success(result.get("message", "Done!"))
                st.rerun()

    st.markdown("---")
    st.markdown(f"<div style='font-size:0.68rem;color:#889063;'>Updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC</div>", unsafe_allow_html=True)


# ── Main header ────────────────────────────────────────────────────────────────
health = api_health()
badge = (f'<span class="api-badge api-ok">API ✓  {health["total_papers"]} papers</span>'
         if health else '<span class="api-badge api-down">API offline</span>')

st.markdown(f"""
<div class="main-header">
  <h1>AI Research Intelligence {badge}</h1>
  <div class="subtitle">Daily distillation of arXiv · Powered by Grok · REST API :8000</div>
</div>
""", unsafe_allow_html=True)

if not health:
    st.info("Start the API: `uvicorn api.main:app --reload --port 8000`")
    st.stop()

# ── Fetch papers via API ───────────────────────────────────────────────────────
params: dict = {"sort_by": sort_by, "limit": 50}
if selected_tags: params["tags"] = ",".join(selected_tags)
if custom_query:  params["query"] = custom_query

data   = api_get("/papers", params=params)
papers = data["papers"] if data else []
total  = data["total"]  if data else 0

st.markdown(f"""
<div class="stats-bar">
  <div class="chip">📄 {health.get('total_papers',0)} stored</div>
  <div class="chip">🔍 {total} matched</div>
  <div class="chip">🌐 v{health.get('api_version','1.0.0')}</div>
</div>
""", unsafe_allow_html=True)

if not papers:
    st.markdown('<div class="empty-state"><h3>No papers yet</h3><p>Hit <strong>Fetch &amp; Analyze</strong> in the sidebar.</p></div>', unsafe_allow_html=True)
    st.stop()


# ── Helpers ────────────────────────────────────────────────────────────────────
def badge_cls(s): return "hi" if s>=8 else ("mid" if s>=6 else "")
def tags_html(tags): return "".join(f'<span class="ctag">{t}</span>' for t in tags)
def authors_str(a): return (", ".join(a[:3]) + " et al." if len(a)>3 else ", ".join(a[:3]))
def bullets(items): return "".join(f"<li>{i}</li>" for i in items) if items else "<li>Not available</li>"


# ── Tabs ───────────────────────────────────────────────────────────────────────
tab_quick, tab_deep, tab_builder, tab_trends, tab_api = st.tabs([
    "⚡ Quick", "🔬 Deep Dive", "🛠 Builder", "📈 Trends", "🔌 API"
])

with tab_quick:
    for i, p in enumerate(papers[:top_n]):
        s = p.get("final_score", 0)
        st.markdown(f"""
        <div class="paper-card {'top' if i==0 else ''}">
          <div class="score-badge {badge_cls(s)}">{s:.1f}</div>
          <div class="card-title">{p['title']}</div>
          <div class="card-meta">{authors_str(p.get('authors',[]))} · {p.get('published','')}</div>
          {tags_html(p.get('tags',[]))}
          <div class="why-matters">🔥 {p.get('why_it_matters') or 'N/A'}</div>
          <span class="sec-label">Key idea</span>
          <div class="sec-body">{p.get('key_idea') or 'Not available'}</div>
          <a class="card-link" href="{p.get('link','#')}" target="_blank">→ Read on arXiv</a>
        </div>""", unsafe_allow_html=True)

with tab_deep:
    for p in papers[:top_n]:
        s = p.get("final_score", 0)
        st.markdown(f"""
        <div class="paper-card">
          <div class="score-badge {badge_cls(s)}">{s:.1f}</div>
          <div class="card-title">{p['title']}</div>
          <div class="card-meta">{authors_str(p.get('authors',[]))} · {p.get('published','')}</div>
          {tags_html(p.get('tags',[]))}
          <div class="why-matters">🔥 {p.get('why_it_matters') or 'N/A'}</div>
          <div style="margin-top:0.7rem;"><span class="sec-label">Core problem</span><div class="sec-body">{p.get('core_problem') or 'N/A'}</div></div>
          <div style="margin-top:0.7rem;"><span class="sec-label">⚙️ Method</span><div class="sec-body"><ul>{bullets(p.get('method_breakdown'))}</ul></div></div>
          <div style="margin-top:0.7rem;"><span class="sec-label">📊 Results</span><div class="sec-body"><ul>{bullets(p.get('results'))}</ul></div></div>
          <div style="margin-top:0.7rem;"><span class="sec-label">⚠️ Limitations</span><div class="sec-body"><ul>{bullets(p.get('limitations'))}</ul></div></div>
          <div style="margin-top:0.7rem;"><span class="sec-label">⭐ Score breakdown</span>
            <div class="sec-body">{s:.1f}/10 &nbsp;·&nbsp; {p.get('relevance_reason') or ''}</div>
          </div>
          <a class="card-link" href="{p.get('pdf_url','#')}" target="_blank">📄 PDF</a>
          &nbsp;&nbsp;<a class="card-link" href="{p.get('link','#')}" target="_blank">🔗 arXiv</a>
        </div>""", unsafe_allow_html=True)

with tab_builder:
    st.markdown("<p style='font-size:0.82rem;color:#889063;margin-bottom:1rem;'>Implementation-focused — papers you can build from.</p>", unsafe_allow_html=True)
    builder = [p for p in papers if len(p.get("method_breakdown",[]))>=2] or papers
    for p in builder[:top_n]:
        with st.expander(f"🛠 {p['title'][:95]}"):
            st.markdown(f"""
            <div style="padding:0.3rem 0;">
              {tags_html(p.get('tags',[]))}
              <div style="margin-top:0.7rem;"><span class="sec-label">What it does</span><div class="sec-body">{p.get('key_idea') or 'N/A'}</div></div>
              <div style="margin-top:0.7rem;"><span class="sec-label">⚙️ How to implement</span><div class="sec-body"><ul>{bullets(p.get('method_breakdown'))}</ul></div></div>
              <div style="margin-top:0.7rem;"><span class="sec-label">📊 Performance</span><div class="sec-body"><ul>{bullets(p.get('results'))}</ul></div></div>
              <div style="margin-top:0.7rem;"><span class="sec-label">⚠️ Watch out for</span><div class="sec-body"><ul>{bullets(p.get('limitations'))}</ul></div></div>
              <a class="card-link" href="{p.get('pdf_url','#')}" target="_blank">→ Full paper</a>
            </div>""", unsafe_allow_html=True)

with tab_trends:
    trends_data = api_get("/trends")
    if trends_data:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Topic distribution**")
            tc = trends_data.get("tag_counts", {})
            max_v = max(tc.values(), default=1)
            for tag, count in list(tc.items())[:12]:
                pct = int((count / max_v) * 100)
                st.markdown(f'<div class="trend-row"><span class="trend-name">{tag}</span><div class="trend-bg"><div class="trend-fill" style="width:{pct}%"></div></div><span class="trend-val">{count}</span></div>', unsafe_allow_html=True)
        with col2:
            st.markdown("**Avg score by topic**")
            for tag, avg in sorted(trends_data.get("avg_scores_by_tag",{}).items(), key=lambda x:-x[1])[:12]:
                st.markdown(f"<div style='font-size:0.8rem;margin-bottom:5px;'><span style='color:#354024;font-weight:500;width:110px;display:inline-block;'>{tag}</span><span style='color:#889063;font-family:monospace;'>{avg:.1f}/10</span></div>", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("**Publication timeline**")
        for date, count in list(trends_data.get("date_counts",{}).items())[:7]:
            dots = "● " * min(count, 15)
            st.markdown(f"<div style='font-size:0.78rem;margin-bottom:4px;'><span style='font-family:monospace;color:#4C3D19;'>{date}</span><span style='color:#889063;margin-left:1rem;'>{dots}<span style='color:#CFBB99;'>({count})</span></span></div>", unsafe_allow_html=True)

with tab_api:
    st.markdown("#### REST API endpoints")
    st.markdown(f"<p style='font-size:0.82rem;color:#889063;margin-bottom:1.2rem;'>Swagger UI → <code>http://localhost:8000/docs</code> &nbsp;·&nbsp; ReDoc → <code>http://localhost:8000/redoc</code></p>", unsafe_allow_html=True)

    for method, path, desc in [
        ("GET",  "/health",                  "Health check — status, paper count, latest fetch"),
        ("GET",  "/api/v1/papers",           "List papers (params: tags, query, sort_by, limit, offset)"),
        ("POST", "/api/v1/papers/search",    "Advanced search via JSON body"),
        ("GET",  "/api/v1/papers/{id}",      "Get a single paper by MD5 ID"),
        ("POST", "/api/v1/pipeline/run",     "Trigger fetch → extract → score pipeline"),
        ("GET",  "/api/v1/pipeline/status",  "Check if pipeline is running"),
        ("GET",  "/api/v1/trends",           "Tag counts, avg scores, date distribution"),
        ("GET",  "/api/v1/trends/tags",      "Quick tag → count map"),
    ]:
        cls = "ep-get" if method=="GET" else "ep-post"
        st.markdown(f'<div class="endpoint-box"><div><span class="ep-method {cls}">{method}</span><span class="ep-path">{path}</span></div><div class="ep-desc">{desc}</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### Live API test")
    test_ep = st.selectbox("Endpoint", ["/papers?limit=3", "/trends", "/trends/tags", "/pipeline/status"])
    if st.button("▶ Call endpoint"):
        resp = api_get(test_ep)
        if resp: st.json(resp)
