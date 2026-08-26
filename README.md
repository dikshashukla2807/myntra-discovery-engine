# Myntra AI-Powered Product Discovery Engine

Evidence-driven discovery of **opportunity areas** that may influence:

> Wishlist → purchase within 30 days

Built for a NextLeap Product Management project (Myntra · Growth).

This is **not** a sentiment tool, review summarizer, or feature recommender. It does **not** assume the problem is price, fit, quality, notifications, or anything else. Public user-generated content is collected, cleaned, classified, clustered, and traced back to original sources so a PM can choose what to validate in 5–6 interviews.

It also does **not** answer “what feature should Myntra build?” That decision comes after primary research.

**Constraint encoded in scoring notes:** monetary incentives cannot be used as a solution, even if price appears as a barrier in the evidence.

## What you get

A PM dashboard with:

1. Overview
2. Data Explorer
3. Behavioral Signals
4. Opportunity Landscape
5. Segments
6. Evidence Explorer (opportunity → theme → supporting/counter evidence → original source)
7. Research Gaps
8. Interview Planner
9. Pipeline / Data Health
10. Discovery Report (HTML/JSON/CSV export)

Every major insight is classified as **FACT / PATTERN / HYPOTHESIS / OPPORTUNITY**. Associations are described as *observed alongside*, not as causes.

## Dataset labels

| Mode | Banner |
| --- | --- |
| Collected public UGC | **Public-source dataset** — “Public user-generated content collected from source platforms.” |
| Built-in samples | **Demo / Sample Data** — not real user research |

Demo observations use `demo://` URLs and `dataset_label: demo_sample`. They are never mixed into public-source statistics without that label.

The system does **not** claim that Play/App Store/Reddit/YouTube comments are independently verified as genuine.

## Architecture

```
SOURCE COLLECTION → RAW JSONL → VALIDATION → CLEANING → LANGUAGE
 → DEDUPE → SPAM/LOW-VALUE → RELEVANCE → BEHAVIORAL EXTRACTION
 → EMBEDDINGS (TF-IDF) → CLUSTERING → THEMES → OPPORTUNITY SCORING
 → RESEARCH GAPS → INTERVIEW PLAN
```

Each stage writes artifacts under `data/`. `text_original` is never overwritten.

- **Backend:** Python FastAPI (`:43124`)
- **Frontend:** Next.js + TypeScript + Tailwind (`:43125`)
- **AI:** Optional OpenAI-compatible LLM. If no key is present, heuristic classifiers + sklearn clustering still run.
- **YouTube / blocked sources:** CSV/JSON import is supported. Missing records are **not** fabricated.

## Collection targets vs actuals

Targets are caps, not quotas:

| Source | Target | Method |
| --- | --- | --- |
| Google Play (`com.myntra.android`) | ~3,000 | Public reviews via `google-play-scraper` |
| Apple App Store (`id907394059`) | ~1,000 | Public iTunes Customer Reviews RSS |
| Reddit | ~300 | Public search JSON, with PullPush archive fallback if Reddit JSON is blocked |
| YouTube | ~500 | YouTube Data API v3 if `YOUTUBE_API_KEY` is set; otherwise import |

The dashboard always shows collected / retained / analyzed / removed-with-reason.

## Run locally

```bash
python3 -m pip install -r requirements.txt
cp .env.example .env

# Optional: collect public UGC (respects rate limits; does not bypass protections)
PYTHONPATH=. python3 scripts/collect_all.py

# Build labeled demo fixtures (not public-source)
PYTHONPATH=. python3 scripts/build_demo_fixtures.py

# Analyze
PYTHONPATH=. python3 scripts/run_pipeline.py
# or demo only:
PYTHONPATH=. python3 scripts/run_pipeline.py --demo-only

# API
PYTHONPATH=. python3 -m uvicorn backend.api.main:app --host 127.0.0.1 --port 43124

# UI
cd frontend && npm install && npm run dev -- --port 43125 --hostname 127.0.0.1
```

Open `http://127.0.0.1:43125`.

Demo Mode can also be started from **Pipeline / Data Health** in the UI (no API keys required).

## Opportunity ranking formula

Each dimension is 0–100. Composite score is a weighted sum:

| Dimension | Weight |
| --- | --- |
| Evidence strength | 0.12 |
| Frequency | 0.10 |
| Purchase association (non-purchase language co-occurrence) | 0.18 |
| User severity | 0.10 |
| Segment concentration | 0.08 |
| Source diversity | 0.08 |
| Workaround intensity | 0.12 |
| Potential user value | 0.08 |
| Potential business relevance | 0.08 |
| Product solvability (non-monetary) | 0.06 |

The opportunity detail page explains **why this ranked higher than the next one**.

## Environment

See `.env.example`. Never put secrets in the frontend. `OPENAI_API_KEY` and `YOUTUBE_API_KEY` are optional.

## Tests

```bash
PYTHONPATH=. python3 -m pytest tests -q
```

## Project layout

```
backend/   api, models, scrapers, pipeline, ai, analytics
frontend/  Next.js dashboard
data/      raw, clean, processed, fixtures, exports
config/    settings, queries, taxonomies
scripts/   collect, pipeline, demo fixtures
tests/
docs/PHASE1_AUDIT.md
```

## Critical rules this repo enforces

1. Do not assume the underlying user problem.
2. Do not fabricate data, statistics, quotes, or URLs.
3. Trace every major insight to source evidence.
4. Distinguish facts from hypotheses.
5. Do not claim causation from observational public data.
6. Preserve contradictory evidence.
7. Clearly distinguish public-source data from demo/sample data.
8. Identify opportunity areas; primary research validates the chosen problem.
