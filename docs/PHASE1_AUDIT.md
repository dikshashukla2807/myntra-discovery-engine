# Phase 1 — Repository Audit

**Date:** 2026-08-26  
**Repository state:** Empty greenfield (root commit `Initialize project` only).  
**Constraint:** Cloud Agent / New Project session — no human approval loop is available, so this audit is recorded and implementation proceeds from the recommended architecture below.

## 1. Existing files

- Git repository initialized on `main`
- No application source, configs, README, data, or tests
- No `.env`, `package.json`, `pyproject.toml`, or scraper scripts

## 2. Existing architecture

None. This is a new project, not a refactor.

## 3. Existing scraper functionality

None. Google Play, App Store, Reddit, and YouTube collectors must be built.

## 4. Existing AI functionality

None. Classification, extraction, embeddings, clustering, theme naming, and opportunity scoring must be built.

## 5. Existing dependencies

None.

## 6. Existing database / storage

None.

## 7. Reusable components

Nothing to reuse. All collectors, pipeline stages, APIs, and dashboard pages are new.

## 8. Problems in existing implementation

Not applicable (empty repo).

## 9. Recommended architecture

**Split stack, matching the requested layout:**

| Layer | Choice | Why |
| --- | --- | --- |
| Backend | Python FastAPI | Scrapers, JSONL stage artifacts, sklearn clustering, optional LLM |
| Storage | JSONL stage files + SQLite index | Every pipeline stage is inspectable; dashboard queries stay fast |
| Frontend | Next.js (App Router) + TypeScript + Tailwind + shadcn/ui | Professional PM dashboard, 9 pages |
| AI | Optional LLM (`OPENAI_API_KEY`) with heuristic fallback | Demo Mode works with zero keys |
| Embeddings | TF-IDF + TruncatedSVD when no embedding API is configured | Deterministic, local, no fabricated insights |
| Dataset labels | `public_source` vs `demo_sample` | Never mix unlabeled synthetic text with public UGC |

**Pipeline stages (each writes its own artifact):**

```
collection → raw JSONL
  → validation → cleaning → language → duplicates → spam/low-value
  → relevance → behavioral extraction → embeddings → clustering
  → theme discovery → opportunity scoring → research gaps → interview plan
```

**Critical rules encoded in the system:**

- Never overwrite `text_original`
- Never fabricate quotes, URLs, or statistics
- Never mark relevance solely because the text contains “Myntra”
- Distinguish FACT / PATTERN / HYPOTHESIS / OPPORTUNITY
- Preserve supporting **and** counter-evidence
- Do not recommend a product feature as the output of discovery

## 10. Implementation plan (executed in this session)

1. Canonical observation schema + quality/exclusion records
2. Google Play collector (`com.myntra.android`) with pagination
3. App Store RSS/JSON collector + CSV/JSON import
4. Reddit public-search collector across behavioral query categories
5. YouTube collector (API if keyed) + CSV/JSON import
6. Data quality, relevance, extraction, clustering, scoring
7. FastAPI for dashboard, exports, interview planner
8. Nine-page PM dashboard with evidence drill-down
9. Demo Mode (labeled) + public-source dataset (labeled)
10. Tests, README, local run instructions

**Targets vs. guarantees:** ~3,000 Play / ~1,000 App Store / ~300 Reddit / ~500 YouTube. Actual collected/retained/analyzed counts are reported; missing records are never fabricated.
