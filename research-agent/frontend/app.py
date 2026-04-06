"""
frontend/app.py — Revamped dark neon-pink UI.
Palette from provided assets:
  Black:        #000000
  Charcoal:     #0D0D0D
  Deep Magenta: #10090E
  Mulberry:     #824261
  Rose/Neon:    #B06B96  →  accent neon: #FF2D78  (vivid pink)
  Amaranth:     #3F0B2F
  Ebony Plum:   #590E41
  Cherry Blossom:#FADCD5 (light text)
"""

import streamlit as st
import requests
from datetime import datetime

API_BASE   = "http://localhost:8000/api/v1"
HEALTH_URL = "http://localhost:8000/health"

# ── API helpers ────────────────────────────────────────────────────────────────
def api_get(path, params=None):
    try:
        r = requests.get(f"{API_BASE}{path}", params=params, timeout=30)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        st.error("API offline — run: uvicorn api.main:app --reload --port 8000")
        return None
    except Exception as e:
        st.error(f"API error: {e}")
        return None

def api_post(path, body=None):
    try:
        r = requests.post(f"{API_BASE}{path}", json=body or {}, timeout=120)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        st.error("API offline — run: uvicorn api.main:app --reload --port 8000")
        return None
    except Exception as e:
        st.error(f"API error: {e}")
        return None

def api_health():
    try:
        r = requests.get(HEALTH_URL, timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Arxiv Intelligence",
    page_icon="A",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=IBM+Plex+Mono:wght@300;400;500&family=Manrope:wght@300;400;500;600&display=swap');

:root {
  --black:     #000000;
  --charcoal:  #0D0D0D;
  --deep-mag:  #10090E;
  --plum:      #590E41;
  --mulberry:  #824261;
  --neon:      #FF2D78;
  --neon-dim:  #C4185A;
  --neon-glow: rgba(255,45,120,0.15);
  --rose:      #B06B96;
  --blush:     #FADCD5;
  --text:      #F0E8F0;
  --muted:     #7A6478;
}

html, body, [class*="css"] {
  font-family: 'Manrope', sans-serif;
  background: #000;
  color: var(--text);
}
.stApp {
  background:
    radial-gradient(ellipse 90% 55% at 75% -5%, rgba(255,45,120,0.28) 0%, transparent 60%),
    radial-gradient(ellipse 70% 50% at 5% 85%, rgba(89,14,65,0.40) 0%, transparent 55%),
    radial-gradient(ellipse 55% 65% at 95% 95%, rgba(130,66,97,0.20) 0%, transparent 50%),
    #000 !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #0f050d 0%, #0D0D0D 40%, #0a0812 100%) !important;
  border-right: 1px solid rgba(255,45,120,0.12) !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }
[data-testid="stSidebar"] .stMarkdown h2 {
  font-family: 'Syne', sans-serif !important;
  font-size: 1.1rem !important;
  font-weight: 800 !important;
  letter-spacing: 0.12em !important;
  text-transform: uppercase !important;
  color: var(--neon) !important;
}
[data-testid="stSidebar"] label {
  font-size: 0.65rem !important;
  font-weight: 600 !important;
  letter-spacing: 0.15em !important;
  text-transform: uppercase !important;
  color: var(--muted) !important;
}
[data-testid="stSidebar"] .stButton button {
  background: transparent !important;
  border: 1px solid var(--neon) !important;
  color: var(--neon) !important;
  border-radius: 2px !important;
  font-family: 'IBM Plex Mono', monospace !important;
  font-size: 0.7rem !important;
  font-weight: 500 !important;
  letter-spacing: 0.1em !important;
  text-transform: uppercase !important;
  width: 100% !important;
  padding: 0.55rem 1rem !important;
  transition: all 0.2s !important;
}
[data-testid="stSidebar"] .stButton button:hover {
  background: var(--neon) !important;
  color: #000 !important;
}
[data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] {
  background: var(--plum) !important;
  border: 1px solid var(--neon-dim) !important;
  border-radius: 2px !important;
}
[data-testid="stSidebar"] .stTextInput input {
  background: #0a0a0a !important;
  border: 1px solid #2a1525 !important;
  border-radius: 2px !important;
  color: var(--text) !important;
  font-family: 'IBM Plex Mono', monospace !important;
  font-size: 0.78rem !important;
}
[data-testid="stSidebar"] .stTextInput input:focus {
  border-color: var(--neon) !important;
}

/* Main header */
.hdr {
  padding: 2.5rem 0 1.5rem;
  border-bottom: 1px solid rgba(255,45,120,0.15);
  margin-bottom: 2rem;
  position: relative;
}
.hdr::after {
  content: '';
  position: absolute;
  bottom: -1px; left: 0; right: 0;
  height: 1px;
  background: linear-gradient(90deg, var(--neon) 0%, transparent 60%);
}
.hdr-eyebrow {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.65rem;
  letter-spacing: 0.25em;
  text-transform: uppercase;
  color: var(--neon);
  margin-bottom: 0.5rem;
}
.hdr-title {
  font-family: 'Syne', sans-serif;
  font-size: 2.6rem;
  font-weight: 800;
  color: var(--text);
  line-height: 1.05;
  letter-spacing: -0.02em;
  margin: 0;
}
.hdr-title span { color: var(--neon); }
.hdr-sub {
  font-size: 0.78rem;
  color: var(--muted);
  font-weight: 400;
  margin-top: 0.5rem;
  letter-spacing: 0.04em;
}

/* API badge */
.api-ok   { display:inline-block; font-family:'IBM Plex Mono',monospace; font-size:0.6rem; padding:2px 8px; border-radius:2px; background:rgba(255,45,120,0.1); color:var(--neon); border:1px solid var(--neon-dim); margin-left:1rem; vertical-align:middle; }
.api-down { display:inline-block; font-family:'IBM Plex Mono',monospace; font-size:0.6rem; padding:2px 8px; border-radius:2px; background:#1a0000; color:#ff4444; border:1px solid #440000; margin-left:1rem; vertical-align:middle; }

/* Stat chips */
.chips { display:flex; gap:0.6rem; margin-bottom:1.8rem; flex-wrap:wrap; }
.chip {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.62rem;
  letter-spacing: 0.08em;
  padding: 4px 12px;
  border: 1px solid #2a1525;
  border-radius: 2px;
  color: var(--muted);
  background: rgba(255,45,120,0.05);
}
.chip b { color: var(--neon); font-weight: 500; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
  background: transparent !important;
  border-bottom: 1px solid #1a0f18 !important;
  gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
  background: transparent !important;
  color: var(--muted) !important;
  font-family: 'IBM Plex Mono', monospace !important;
  font-size: 0.65rem !important;
  letter-spacing: 0.15em !important;
  text-transform: uppercase !important;
  padding: 0.6rem 1.4rem !important;
  border: none !important;
  border-bottom: 2px solid transparent !important;
  border-radius: 0 !important;
}
.stTabs [aria-selected="true"] {
  color: var(--neon) !important;
  border-bottom: 2px solid var(--neon) !important;
}

/* Paper card */
.card {
  background: linear-gradient(135deg, rgba(255,45,120,0.07) 0%, rgba(89,14,65,0.18) 40%, rgba(13,13,13,0.95) 100%);
  border: 1px solid rgba(255,45,120,0.18);
  border-left: 3px solid var(--neon);
  border-radius: 10px;
  padding: 1.6rem 1.8rem;
  margin-bottom: 2px;
  position: relative;
  transition: border-color 0.2s, background 0.2s, box-shadow 0.2s;
  box-shadow: 0 0 0 transparent;
}
.card:hover {
  background: linear-gradient(135deg, rgba(255,45,120,0.13) 0%, rgba(89,14,65,0.28) 40%, rgba(16,9,14,0.98) 100%);
  border-color: rgba(255,45,120,0.35);
  border-left-color: var(--neon);
  box-shadow: 0 0 30px rgba(255,45,120,0.08), inset 0 0 30px rgba(255,45,120,0.03);
}
.card.dim {
  background: linear-gradient(135deg, rgba(130,66,97,0.06) 0%, rgba(63,11,47,0.20) 40%, rgba(13,13,13,0.95) 100%);
  border-left-color: var(--mulberry);
  border-color: rgba(130,66,97,0.15);
}

.score-badge {
  position: absolute;
  top: 1.4rem; right: 1.6rem;
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--neon);
  letter-spacing: 0.05em;
}
.score-badge.hi { color: var(--neon); }
.score-badge.mid { color: var(--rose); }
.score-badge.lo  { color: var(--muted); }

.card-title {
  font-family: 'Syne', sans-serif;
  font-size: 1rem;
  font-weight: 700;
  color: var(--text);
  margin: 0 4rem 0.3rem 0;
  line-height: 1.35;
  letter-spacing: -0.01em;
}
.card-meta {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.62rem;
  color: var(--muted);
  letter-spacing: 0.06em;
  margin-bottom: 0.9rem;
}

.tag {
  display: inline-block;
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.58rem;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--neon-dim);
  border: 1px solid #3a1030;
  padding: 1px 6px;
  margin: 0 3px 4px 0;
  border-radius: 1px;
}

.why {
  font-size: 0.85rem;
  color: var(--blush);
  font-style: italic;
  border-left: 2px solid var(--neon);
  padding: 0.5rem 0.9rem;
  margin: 0.8rem 0;
  font-family: 'Manrope', sans-serif;
  line-height: 1.6;
  background: linear-gradient(90deg, rgba(255,45,120,0.07) 0%, transparent 100%);
}

.sec-label {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.58rem;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--neon-dim);
  display: block;
  margin-bottom: 4px;
  margin-top: 0.8rem;
}
.sec-body {
  font-size: 0.82rem;
  color: #c8b8c4;
  line-height: 1.7;
}
.sec-body ul { padding-left: 1rem; margin: 0; }
.sec-body li { margin-bottom: 3px; }

.card-link {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.65rem;
  color: var(--neon-dim);
  text-decoration: none;
  letter-spacing: 0.08em;
  border-bottom: 1px solid #3a1030;
  display: inline-block;
  margin-top: 0.8rem;
  transition: color 0.15s, border-color 0.15s;
}
.card-link:hover { color: var(--neon); border-bottom-color: var(--neon); }

/* Empty state */
.empty {
  text-align: center;
  padding: 6rem 2rem;
  border: 1px dashed #1a0f18;
}
.empty h3 {
  font-family: 'Syne', sans-serif;
  font-size: 1.4rem;
  font-weight: 800;
  color: var(--neon);
  margin-bottom: 0.5rem;
  letter-spacing: -0.02em;
}
.empty p { font-size: 0.82rem; color: var(--muted); }

/* Trend bars */
.t-row { display:flex; align-items:center; gap:10px; margin-bottom:8px; }
.t-name { font-family:'IBM Plex Mono',monospace; font-size:0.7rem; color:var(--text); width:120px; flex-shrink:0; letter-spacing:0.04em; }
.t-bg { flex:1; background:#1a0f18; border-radius:0; height:3px; }
.t-fill { height:3px; background:var(--neon); }
.t-val { font-family:'IBM Plex Mono',monospace; font-size:0.65rem; color:var(--muted); width:28px; text-align:right; }

/* API explorer */
.ep {
  background: var(--charcoal);
  border: 1px solid #1a0f18;
  padding: 0.8rem 1.1rem;
  margin-bottom: 1px;
  display: flex;
  align-items: baseline;
  gap: 0.8rem;
}
.ep-get  { font-family:'IBM Plex Mono',monospace; font-size:0.6rem; color:#00ffaa; letter-spacing:0.1em; }
.ep-post { font-family:'IBM Plex Mono',monospace; font-size:0.6rem; color:var(--neon); letter-spacing:0.1em; }
.ep-path { font-family:'IBM Plex Mono',monospace; font-size:0.75rem; color:var(--text); flex:1; }
.ep-desc { font-size:0.72rem; color:var(--muted); }

/* Global button */
.stButton > button {
  background: transparent !important;
  border: 1px solid var(--neon) !important;
  color: var(--neon) !important;
  border-radius: 2px !important;
  font-family: 'IBM Plex Mono', monospace !important;
  font-size: 0.7rem !important;
  letter-spacing: 0.1em !important;
  text-transform: uppercase !important;
  padding: 0.5rem 1.4rem !important;
  transition: all 0.2s !important;
}
.stButton > button:hover {
  background: var(--neon) !important;
  color: #000 !important;
}

/* Expander */
.streamlit-expanderHeader {
  font-family: 'IBM Plex Mono', monospace !important;
  font-size: 0.72rem !important;
  color: var(--muted) !important;
  letter-spacing: 0.08em !important;
  text-transform: uppercase !important;
  background: var(--charcoal) !important;
  border: 1px solid #1a0f18 !important;
}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ARXIV INTEL")
    st.markdown("---")

    st.markdown("**TOPICS**")
    ALL_TAGS = ["LLM","Agents","RAG","Computer Vision","NLP","Multimodal",
                "Efficiency","Robotics","Reasoning","Fine-tuning","Benchmarks","Safety","Diffusion"]
    selected_tags = st.multiselect("Topics", options=ALL_TAGS, default=[], label_visibility="collapsed")

    st.markdown("**SEARCH**")
    custom_query = st.text_input("Search", placeholder="keyword or concept...", label_visibility="collapsed")

    st.markdown("**SORT**")
    sort_by = st.radio("Sort", options=["final_score","published","relevance_score"],
        format_func=lambda x: {"final_score":"Score","published":"Date","relevance_score":"LLM"}[x],
        label_visibility="collapsed")

    st.markdown("---")
    st.markdown("**PIPELINE**")
    max_fetch = st.slider("Fetch", 5, 20, 10, label_visibility="visible")
    top_n     = st.slider("Keep top N", 3, 12, 6, label_visibility="visible")
    skip_seen = st.checkbox("Skip seen", value=True)

    if st.button("search"):
        with st.spinner("Fetching + analyzing..."):
            result = api_post("/pipeline/run", {"max_fetch":max_fetch,"top_n":top_n,"skip_seen":skip_seen})
            if result:
                st.success(result.get("message","Done"))
                st.rerun()

    st.markdown("---")
    st.markdown(f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.58rem;color:#3a2535;letter-spacing:0.1em;">{datetime.utcnow().strftime("%Y-%m-%d %H:%M")} UTC</div>', unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────────
health = api_health()
badge  = '<span class="api-ok">ONLINE</span>' if health else '<span class="api-down">OFFLINE</span>'

st.markdown(f"""
<div class="hdr">
  <div class="hdr-eyebrow">AI Research Intelligence</div>
  <h1 class="hdr-title">Daily <span>arXiv</span> Digest {badge}</h1>
  <div class="hdr-sub">Structured extraction &nbsp;/&nbsp; Relevance scoring &nbsp;/&nbsp; Gemini 2.5 Flash &nbsp;/&nbsp; REST :8000</div>
</div>
""", unsafe_allow_html=True)

if not health:
    st.markdown('<div class="empty"><h3>API Offline</h3><p>uvicorn api.main:app --reload --port 8000</p></div>', unsafe_allow_html=True)
    st.stop()

# ── Load papers ────────────────────────────────────────────────────────────────
params = {"sort_by": sort_by, "limit": 50}
if selected_tags: params["tags"] = ",".join(selected_tags)
if custom_query:  params["query"] = custom_query

data   = api_get("/papers", params=params)
papers = data["papers"] if data else []
total  = data["total"]  if data else 0

st.markdown(f"""
<div class="chips">
  <div class="chip"><b>{health.get('total_papers',0)}</b> stored</div>
  <div class="chip"><b>{total}</b> matched</div>
  <div class="chip">v{health.get('api_version','1.0')}</div>
</div>
""", unsafe_allow_html=True)

if not papers:
    st.markdown('<div class="empty"><h3>No Papers</h3><p>Run the pipeline to fetch and analyze the latest arXiv papers.</p></div>', unsafe_allow_html=True)
    st.stop()

# ── Helpers ────────────────────────────────────────────────────────────────────
def sc(s):
    return "hi" if s>=8 else ("mid" if s>=6 else "lo")

def tags_html(tags):
    return "".join(f'<span class="tag">{t}</span>' for t in tags)

def authors(a):
    s = ", ".join(a[:3])
    return s + " et al." if len(a)>3 else s

def bul(items):
    return "".join(f"<li>{i}</li>" for i in items) if items else "<li>—</li>"

# ── Tabs ───────────────────────────────────────────────────────────────────────
t1, t2, t3, t4, t5 = st.tabs(["QUICK", "DEEP DIVE", "BUILDER", "TRENDS", "API"])

# QUICK
with t1:
    for i, p in enumerate(papers[:top_n]):
        s = p.get("final_score", 0)
        st.markdown(f"""
        <div class="card {'dim' if i>0 else ''}">
          <div class="score-badge {sc(s)}">{s:.1f}</div>
          <div class="card-title">{p['title']}</div>
          <div class="card-meta">{authors(p.get('authors',[]))} &nbsp;·&nbsp; {p.get('published','')}</div>
          {tags_html(p.get('tags',[]))}
          <div class="why">{p.get('why_it_matters') or 'No summary available.'}</div>
          <span class="sec-label">Key idea</span>
          <div class="sec-body">{p.get('key_idea') or '—'}</div>
          <a class="card-link" href="{p.get('link','#')}" target="_blank">READ ON ARXIV &rarr;</a>
        </div>
        """, unsafe_allow_html=True)

# DEEP DIVE
with t2:
    for p in papers[:top_n]:
        s = p.get("final_score", 0)
        st.markdown(f"""
        <div class="card">
          <div class="score-badge {sc(s)}">{s:.1f}</div>
          <div class="card-title">{p['title']}</div>
          <div class="card-meta">{authors(p.get('authors',[]))} &nbsp;·&nbsp; {p.get('published','')}</div>
          {tags_html(p.get('tags',[]))}
          <div class="why">{p.get('why_it_matters') or '—'}</div>
          <span class="sec-label">Core Problem</span>
          <div class="sec-body">{p.get('core_problem') or '—'}</div>
          <span class="sec-label">Method</span>
          <div class="sec-body"><ul>{bul(p.get('method_breakdown'))}</ul></div>
          <span class="sec-label">Results</span>
          <div class="sec-body"><ul>{bul(p.get('results'))}</ul></div>
          <span class="sec-label">Limitations</span>
          <div class="sec-body"><ul>{bul(p.get('limitations'))}</ul></div>
          <span class="sec-label">Relevance</span>
          <div class="sec-body">{s:.1f}/10 &mdash; {p.get('relevance_reason') or ''}</div>
          <a class="card-link" href="{p.get('pdf_url','#')}" target="_blank">PDF &rarr;</a>
          &nbsp;&nbsp;
          <a class="card-link" href="{p.get('link','#')}" target="_blank">ARXIV &rarr;</a>
        </div>
        """, unsafe_allow_html=True)

# BUILDER
with t3:
    st.markdown('<p style="font-family:\'IBM Plex Mono\',monospace;font-size:0.65rem;color:#3a2535;letter-spacing:0.1em;margin-bottom:1.2rem;">IMPLEMENTATION-FOCUSED VIEW</p>', unsafe_allow_html=True)
    bl = [p for p in papers if len(p.get("method_breakdown",[]))>=2] or papers
    for p in bl[:top_n]:
        with st.expander(p['title'][:95]):
            st.markdown(f"""
            <div style="padding:0.3rem 0;">
              {tags_html(p.get('tags',[]))}
              <span class="sec-label">What it does</span>
              <div class="sec-body">{p.get('key_idea') or '—'}</div>
              <span class="sec-label">How to implement</span>
              <div class="sec-body"><ul>{bul(p.get('method_breakdown'))}</ul></div>
              <span class="sec-label">Reported performance</span>
              <div class="sec-body"><ul>{bul(p.get('results'))}</ul></div>
              <span class="sec-label">Watch out for</span>
              <div class="sec-body"><ul>{bul(p.get('limitations'))}</ul></div>
              <a class="card-link" href="{p.get('pdf_url','#')}" target="_blank">FULL PAPER &rarr;</a>
            </div>
            """, unsafe_allow_html=True)

# TRENDS
with t4:
    td = api_get("/trends")
    if td:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<p class="sec-label" style="margin-bottom:1rem;">Topic Distribution</p>', unsafe_allow_html=True)
            tc = td.get("tag_counts", {})
            mx = max(tc.values(), default=1)
            for tag, count in list(tc.items())[:12]:
                pct = int((count/mx)*100)
                st.markdown(f'<div class="t-row"><span class="t-name">{tag}</span><div class="t-bg"><div class="t-fill" style="width:{pct}%"></div></div><span class="t-val">{count}</span></div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<p class="sec-label" style="margin-bottom:1rem;">Avg Score by Topic</p>', unsafe_allow_html=True)
            for tag, avg in sorted(td.get("avg_scores_by_tag",{}).items(), key=lambda x:-x[1])[:12]:
                st.markdown(f'<div style="display:flex;justify-content:space-between;margin-bottom:6px;"><span style="font-family:\'IBM Plex Mono\',monospace;font-size:0.7rem;color:#c8b8c4;">{tag}</span><span style="font-family:\'IBM Plex Mono\',monospace;font-size:0.7rem;color:var(--neon);">{avg:.1f}</span></div>', unsafe_allow_html=True)
        st.markdown('<div style="height:1px;background:#1a0f18;margin:1.5rem 0;"></div>', unsafe_allow_html=True)
        st.markdown('<p class="sec-label" style="margin-bottom:1rem;">Publication Timeline</p>', unsafe_allow_html=True)
        for date, cnt in list(td.get("date_counts",{}).items())[:7]:
            bar = "—" * min(cnt, 20)
            st.markdown(f'<div style="display:flex;gap:1.5rem;margin-bottom:5px;font-family:\'IBM Plex Mono\',monospace;font-size:0.65rem;"><span style="color:#3a2535;width:90px;">{date}</span><span style="color:var(--neon-dim);">{bar}</span><span style="color:var(--muted);">({cnt})</span></div>', unsafe_allow_html=True)

# API
with t5:
    st.markdown(f'<p class="sec-label" style="margin-bottom:1rem;">Swagger: <span style="color:var(--text);">localhost:8000/docs</span> &nbsp;·&nbsp; ReDoc: <span style="color:var(--text);">localhost:8000/redoc</span></p>', unsafe_allow_html=True)
    for method, path, desc in [
        ("GET",  "/health",                  "Health check"),
        ("GET",  "/api/v1/papers",           "List papers — tags, query, sort_by, limit, offset"),
        ("POST", "/api/v1/papers/search",    "Advanced search via JSON body"),
        ("GET",  "/api/v1/papers/{id}",      "Single paper by ID"),
        ("POST", "/api/v1/pipeline/run",     "Trigger fetch + extract + score"),
        ("GET",  "/api/v1/pipeline/status",  "Pipeline running status"),
        ("GET",  "/api/v1/trends",           "Analytics: tag counts, scores, timeline"),
        ("GET",  "/api/v1/trends/tags",      "Tag frequency map"),
    ]:
        cls = "ep-get" if method=="GET" else "ep-post"
        st.markdown(f'<div class="ep"><span class="{cls}">{method}</span><span class="ep-path">{path}</span><span class="ep-desc">{desc}</span></div>', unsafe_allow_html=True)

    st.markdown('<div style="height:1.5rem;"></div>', unsafe_allow_html=True)
    st.markdown('<p class="sec-label">Live Test</p>', unsafe_allow_html=True)
    ep = st.selectbox("Endpoint", ["/papers?limit=3", "/trends", "/trends/tags", "/pipeline/status"], label_visibility="collapsed")
    if st.button("CALL"):
        resp = api_get(ep)
        if resp: st.json(resp)
