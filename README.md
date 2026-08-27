# Myntra AI-Powered Product Discovery Engine

Evidence-driven discovery of **opportunity areas** that may influence:

> Wishlist → purchase within 30 days

Built for a NextLeap Product Management project (Myntra · Growth).

This is **not** a sentiment tool, review summarizer, or feature recommender. It does **not** assume the problem is price, fit, quality, notifications, or anything else. Public user-generated content is collected, cleaned, classified, clustered, and traced back to original sources so a PM can choose what to validate in 5–6 interviews.

It also does **not** answer “what feature should Myntra build?” That decision comes after primary research.

**Constraint encoded in scoring notes:** monetary incentives cannot be used as a solution, even if price appears as a barrier in the evidence.

## What you get

A 5-page PM research tool:

1. Overview — funnel, source counts, top opportunities
2. Evidence Explorer — original comments + extraction + source URL
3. Opportunity Landscape — ranked table
4. Opportunity detail — evidence, quantification, counter-evidence, gap
5. Research handoff — what we know / don’t / interview questions

It stops at **opportunity + evidence + research gap**. It does not recommend a feature.

Associations are described as *observed alongside*, not as causes.

## Dataset labels

| Mode | Banner |
| --- | --- |
| Collected public UGC | **Public-source dataset** — “Public user-generated content collected from source platforms.” |
| Built-in samples | **Demo / Sample Data** — not real user research |

Demo observations use `demo://` URLs and `dataset_label: demo_sample`. They are never mixed into public-source statistics without that label.

The system does **not** claim that Play/App Store/Reddit/YouTube comments are independently verified as genuine.

## Architecture

```
PUBLIC UGC → COLLECT → CLEAN + DEDUPE → RELEVANCE → BEHAVIORAL EXTRACTION
 → THEMES (5–10) → QUANTIFY IN CODE → RANK (six scores, 1–5)
 → EVIDENCE + COUNTER-EVIDENCE → RESEARCH HANDOFF
```

`text_original` is never overwritten. Demo analysis is stored in `data/processed_demo/` so it cannot overwrite public-source results.

- **Backend:** Python FastAPI (`:43124`)
- **Frontend:** Next.js + TypeScript + Tailwind (`:43125`)
- **AI:** Optional LLM. Without a key, heuristics + TF-IDF clustering still run.
- **Default sources:** Google Play + Reddit. YouTube via API or import. App Store collector is optional.

## Collection targets vs actuals

Targets are caps, not quotas:

| Source | Target | Method |
| --- | --- | --- |
| Google Play (`com.myntra.android`) | ~3,000 | Public reviews via `google-play-scraper` |
| Reddit | ~300 | Public archive when live Reddit JSON is blocked |
| YouTube | ~500 | API if keyed; otherwise import. Never fabricated |
| App Store | optional | Collector exists; not part of the default workflow |

The dashboard shows collected → duplicates/low-value removed → irrelevant removed → relevant.

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

Open `http://127.0.0.1:43125`. Switch **Demo / sample data** on Overview if `processed_demo` exists.

## Opportunity ranking

Each dimension is **1–5**. Composite is a weighted average (max 5):

| Dimension | Weight |
| --- | --- |
| Evidence strength | 0.20 |
| Frequency | 0.15 |
| Purchase association (postponed / abandoned / bought alternative) | 0.25 |
| User severity | 0.15 |
| Workaround intensity | 0.15 |
| Segment relevance | 0.10 |

The opportunity page explains why one rank beat the next.

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
