# 🌿 AI Research Intelligence Agent

A daily digest of the latest AI/ML papers from arXiv — extracted, scored, and presented beautifully using the **Grok API**.

![Python](https://img.shields.io/badge/Python-3.11-4C3D19?style=flat&logo=python)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-354024?style=flat&logo=streamlit)
![Grok](https://img.shields.io/badge/LLM-Grok_xAI-889063?style=flat)

---

## ✨ Features

| Feature | Details |
|---|---|
| 📡 **Paper Retrieval** | Fetches from arXiv: `cs.AI`, `cs.LG`, `cs.CL`, `cs.CV` |
| 🧠 **Structured Extraction** | Grok API extracts: problem, idea, method, results, limitations |
| 🏷 **Auto-tagging** | LLM + keyword matching across 13 topics |
| ⭐ **Relevance Scoring** | Weighted: LLM (40%) + Recency (35%) + Keywords (25%) |
| 🎨 **4 View Modes** | Quick · Deep Dive · Builder · Trends |
| 🔍 **Personalization** | Filter by topic + custom search query |
| ♻️ **Dedup** | Never shows the same paper twice |
| ⏰ **Auto-refresh** | GitHub Actions runs the pipeline daily |

---

## 🚀 Quickstart

### 1. Clone & install

```bash
git clone https://github.com/your-username/research-agent
cd research-agent
pip install -r requirements.txt
```

### 2. Set up your API key

```bash
cp .env.example .env
# Edit .env and add your Grok API key:
# GROK_API_KEY=your_key_here
```

Get your Grok API key at: https://console.x.ai/

### 3. Fetch papers

```bash
python backend/pipeline.py --max 20 --top 10
```

Options:
- `--max` — how many papers to fetch from arXiv (default: 20)
- `--top` — how many top papers to keep after scoring (default: 10)
- `--fresh` — ignore deduplication and refetch all

### 4. Launch the UI

```bash
streamlit run frontend/app.py
```

Open http://localhost:8501

---

## 🗂 Project Structure

```
research-agent/
│
├── backend/
│   ├── fetch_papers.py     # arXiv integration
│   ├── extractor.py        # Grok API extraction
│   ├── tagger.py           # Tag assignment
│   ├── scorer.py           # Relevance scoring
│   ├── pipeline.py         # Orchestration
│   └── utils.py            # Storage & filtering
│
├── frontend/
│   └── app.py              # Streamlit UI
│
├── data/
│   ├── papers.json         # Stored enriched papers
│   └── seen.json           # Dedup tracking
│
├── .github/workflows/
│   └── daily.yml           # Automated daily fetch
│
├── requirements.txt
├── .env.example
└── README.md
```

---

## ⚙️ GitHub Actions (Automated Daily Run)

1. Push this repo to GitHub
2. Go to **Settings → Secrets → Actions**
3. Add secret: `GROK_API_KEY` = your key
4. The workflow in `.github/workflows/daily.yml` runs at **6 AM UTC** and commits updated papers

---

## 🎨 UI Modes

| Mode | Description |
|---|---|
| ⚡ Quick | 3-bullet highlights for fast reading |
| 🔬 Deep Dive | Full breakdown: problem, method, results, limitations |
| 🛠 Builder | Implementation-focused: how to build it |
| 📈 Trends | Topic distribution, score averages, paper timeline |

---

## 🔧 Scoring Formula

```
Final Score = 0.40 × LLM_Score + 0.35 × Recency + 0.25 × Keyword_Match
```

All components are normalized to 0–10.

---

## 🌿 Design

Color palette: **Café Noir · Kombu Green · Moss Green · Tan · Bone**  
Typography: **Playfair Display** (headings) + **DM Sans** (body) + **DM Mono** (code/scores)
