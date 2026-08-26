from __future__ import annotations

import csv
import io
from typing import Any

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse, StreamingResponse

from backend.analytics.interviews import generate_interview_plan
from backend.pipeline.runner import run_pipeline
from backend.scrapers.collect import collect_all
from backend.scrapers.importer import import_observations
from backend.services import store
from backend.utils.io import utc_now
from config import settings

settings.ensure_dirs()

app = FastAPI(
    title="Myntra Discovery Engine",
    description="Evidence-driven discovery of opportunity areas for wishlist → 30-day purchase conversion.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS + ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict[str, Any]:
    return {"ok": True, "time": utc_now(), "banner": store.dataset_banner()}


@app.get("/api/banner")
def banner() -> dict[str, str]:
    return store.dataset_banner()


@app.get("/api/overview")
def overview() -> dict[str, Any]:
    data = store.load_overview()
    data["banner"] = store.dataset_banner()
    data["pipeline"] = store.load_pipeline()
    return data


@app.get("/api/quality")
def quality() -> dict[str, Any]:
    return store.load_quality()


@app.get("/api/pipeline")
def pipeline() -> dict[str, Any]:
    return store.load_pipeline()


@app.get("/api/themes")
def themes() -> list[dict[str, Any]]:
    return store.load_themes()


@app.get("/api/opportunities")
def opportunities(
    sort: str = Query("rank"),
    min_frequency: int = Query(0),
    source: str | None = None,
) -> list[dict[str, Any]]:
    rows = store.load_opportunities()
    if min_frequency:
        rows = [r for r in rows if r.get("frequency", 0) >= min_frequency]
    if source:
        # Filter to opportunities that have evidence from this source via themes
        themes = {t["theme_id"]: t for t in store.load_themes()}
        filtered = []
        for r in rows:
            tids = r.get("theme_ids") or []
            sources = set()
            for tid in tids:
                sources.update((themes.get(tid) or {}).get("source_diversity") or [])
            if source in sources:
                filtered.append(r)
        rows = filtered
    reverse = sort.lstrip("-") != "rank"
    key = sort.lstrip("-")
    if key in {"rank", "frequency", "purchase_association", "evidence_strength", "composite_score", "confidence_score"}:
        rows = sorted(rows, key=lambda r: r.get(key) or 0, reverse=(sort.startswith("-") or key != "rank"))
    return rows


@app.get("/api/opportunities/{opportunity_id}")
def opportunity_detail(opportunity_id: str) -> dict[str, Any]:
    rows = store.load_opportunities()
    match = next((r for r in rows if r["opportunity_id"] == opportunity_id), None)
    if not match:
        raise HTTPException(404, "Opportunity not found")
    themes = [t for t in store.load_themes() if t["theme_id"] in (match.get("theme_ids") or [])]
    ext = store.load_extractions()
    rel_obs = {o["observation_id"]: o for o in store.load_relevant()}

    def pack(ids: list[str]) -> list[dict[str, Any]]:
        out = []
        for oid in ids[:40]:
            obs = rel_obs.get(oid)
            if not obs:
                continue
            out.append(
                {
                    "observation": obs,
                    "extraction": ext.get(oid),
                    "theme_ids": match.get("theme_ids"),
                }
            )
        return out

    return {
        "opportunity": match,
        "themes": themes,
        "supporting": pack(match.get("supporting_evidence_ids") or []),
        "counter": pack(match.get("counter_evidence_ids") or []),
        "banner": store.dataset_banner(),
        "scoring_weights": store.load_pipeline().get("weights"),
    }


@app.get("/api/segments")
def segments() -> list[dict[str, Any]]:
    return store.load_segments()


@app.get("/api/gaps")
def gaps() -> list[dict[str, Any]]:
    return store.load_gaps()


@app.get("/api/signals")
def signals() -> dict[str, Any]:
    overview = store.load_overview()
    return overview.get("behavioral") or {}


@app.get("/api/observations")
def observations(
    source: str | None = None,
    rating: str | None = None,
    q: str | None = None,
    user_intent: str | None = None,
    wishlist_behavior: str | None = None,
    purchase_outcome: str | None = None,
    barrier: str | None = None,
    segment: str | None = None,
    theme: str | None = None,
    external_research: str | None = None,
    dataset_label: str | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> dict[str, Any]:
    rows = store.load_relevant()
    ext = store.load_extractions()
    rel = store.load_relevance()
    clusters = store.load_clusters()
    themes = store.load_themes()
    cluster_to_theme = {t.get("cluster_id"): t for t in themes}

    filtered: list[dict[str, Any]] = []
    for obs in rows:
        e = ext.get(obs["observation_id"]) or {}
        if source and obs.get("source") != source:
            continue
        if dataset_label and obs.get("dataset_label") != dataset_label:
            continue
        if rating and str(obs.get("rating")) != str(rating):
            continue
        if user_intent and e.get("user_intent") != user_intent:
            continue
        if wishlist_behavior and e.get("wishlist_behavior") != wishlist_behavior:
            continue
        if purchase_outcome and e.get("purchase_outcome") != purchase_outcome:
            continue
        if barrier and barrier not in (e.get("barriers") or []):
            continue
        if segment and segment not in (e.get("segment_signals") or []):
            continue
        if external_research == "true" and not e.get("external_research"):
            continue
        if external_research == "false" and e.get("external_research"):
            continue
        cid = clusters.get(obs["observation_id"])
        theme_obj = cluster_to_theme.get(cid)
        if theme and theme_obj and theme not in theme_obj.get("theme_id", "") and theme.lower() not in (theme_obj.get("theme_name") or "").lower():
            continue
        if theme and not theme_obj:
            continue
        if q:
            blob = (obs.get("text_original") or "") + " " + (obs.get("title") or "")
            if q.lower() not in blob.lower():
                continue
        filtered.append(
            {
                "observation": obs,
                "extraction": e,
                "relevance": rel.get(obs["observation_id"]),
                "theme": theme_obj,
                "cluster_id": cid,
            }
        )
    total = len(filtered)
    page = filtered[offset : offset + limit]
    return {"total": total, "offset": offset, "limit": limit, "results": page}


@app.get("/api/evidence/{observation_id}")
def evidence(observation_id: str) -> dict[str, Any]:
    rows = {o["observation_id"]: o for o in store.load_relevant()}
    obs = rows.get(observation_id)
    if not obs:
        raise HTTPException(404, "Observation not found")
    clusters = store.load_clusters()
    themes = store.load_themes()
    cid = clusters.get(observation_id)
    theme = next((t for t in themes if t.get("cluster_id") == cid), None)
    opps = [o for o in store.load_opportunities() if observation_id in (o.get("supporting_evidence_ids") or o.get("counter_evidence_ids") or [])]
    return {
        "observation": obs,
        "extraction": store.load_extractions().get(observation_id),
        "relevance": store.load_relevance().get(observation_id),
        "theme": theme,
        "opportunities": opps,
        "banner": store.dataset_banner(),
    }


@app.post("/api/interviews")
def interviews(body: dict[str, Any]) -> dict[str, Any]:
    opp_id = body.get("opportunity_id")
    segment = body.get("segment")
    opps = store.load_opportunities()
    match = next((o for o in opps if o["opportunity_id"] == opp_id), None)
    if not match:
        raise HTTPException(404, "Select a valid opportunity")
    return generate_interview_plan(match, segment)


@app.get("/api/report")
def report() -> dict[str, Any]:
    return store.load_report()


@app.get("/api/report.html")
def report_html() -> HTMLResponse:
    path = settings.PROCESSED_DIR / "discovery_report.html"
    if not path.exists():
        raise HTTPException(404, "Report not generated yet")
    return HTMLResponse(path.read_text(encoding="utf-8"))


def _csv(rows: list[dict[str, Any]], fieldnames: list[str]) -> StreamingResponse:
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow({k: row.get(k) for k in fieldnames})
    buf.seek(0)
    return StreamingResponse(iter([buf.getvalue()]), media_type="text/csv")


@app.get("/api/export/observations.csv")
def export_obs_csv():
    rows = []
    ext = store.load_extractions()
    for obs in store.load_relevant():
        e = ext.get(obs["observation_id"]) or {}
        rows.append(
            {
                "observation_id": obs["observation_id"],
                "source": obs.get("source"),
                "source_id": obs.get("source_id"),
                "source_url": obs.get("source_url"),
                "date": obs.get("date"),
                "rating": obs.get("rating"),
                "text_original": obs.get("text_original"),
                "language": obs.get("language"),
                "dataset_label": obs.get("dataset_label"),
                "user_intent": e.get("user_intent"),
                "wishlist_behavior": e.get("wishlist_behavior"),
                "purchase_outcome": e.get("purchase_outcome"),
                "barriers": "|".join(e.get("barriers") or []),
                "external_research": e.get("external_research"),
            }
        )
    return _csv(
        rows,
        [
            "observation_id",
            "source",
            "source_id",
            "source_url",
            "date",
            "rating",
            "text_original",
            "language",
            "dataset_label",
            "user_intent",
            "wishlist_behavior",
            "purchase_outcome",
            "barriers",
            "external_research",
        ],
    )


@app.get("/api/export/themes.csv")
def export_themes_csv():
    rows = store.load_themes()
    return _csv(
        rows,
        ["theme_id", "theme_name", "frequency", "frequency_percentage", "confidence", "research_gap", "claim_type"],
    )


@app.get("/api/export/opportunities.csv")
def export_opps_csv():
    rows = store.load_opportunities()
    return _csv(
        rows,
        [
            "rank",
            "opportunity_id",
            "title",
            "frequency",
            "purchase_association",
            "evidence_strength",
            "confidence",
            "composite_score",
            "research_gap",
        ],
    )


@app.get("/api/export/analysis.json")
def export_json():
    return JSONResponse(
        {
            "banner": store.dataset_banner(),
            "quality": store.load_quality(),
            "overview": store.load_overview(),
            "themes": store.load_themes(),
            "opportunities": store.load_opportunities(),
            "segments": store.load_segments(),
            "gaps": store.load_gaps(),
            "report": store.load_report(),
        }
    )


@app.post("/api/pipeline/run")
def pipeline_run(body: dict[str, Any] | None = None):
    body = body or {}
    return run_pipeline(
        include_demo=bool(body.get("include_demo")),
        demo_only=bool(body.get("demo_only")),
        sample_size=int(body.get("sample_size") or 0),
    )


@app.post("/api/collect")
def collect():
    return collect_all()


@app.post("/api/ingest/{source}")
async def ingest(source: str, file: UploadFile = File(...)):
    if source not in {"google_play", "app_store", "reddit", "youtube"}:
        raise HTTPException(400, "Unknown source")
    dest = settings.RAW_DIR / source / file.filename
    dest.write_bytes(await file.read())
    rows = import_observations(dest, default_source=source)
    return {"imported": len(rows), "path": str(dest)}
