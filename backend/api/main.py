from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from backend.analytics.interviews import generate_interview_plan
from backend.services import store
from backend.utils.io import utc_now
from config import settings

settings.ensure_dirs()

app = FastAPI(
    title="Myntra Discovery Engine",
    description="Evidence-driven discovery of opportunity areas for wishlist → 30-day purchase conversion.",
    version="1.1.0",
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
    return {"ok": True, "time": utc_now(), "banner": store.dataset_banner(), "demo_available": store.demo_available()}


@app.get("/api/banner")
def banner() -> dict[str, Any]:
    data = store.dataset_banner()
    data["demo_available"] = store.demo_available()
    return data


@app.post("/api/dataset/mode")
def set_mode(body: dict[str, Any] | None = None) -> dict[str, Any]:
    body = body or {}
    mode = body.get("mode") or "public"
    if mode == "demo" and not store.demo_available():
        raise HTTPException(400, "Demo dataset has not been generated yet.")
    return store.set_mode(mode)


@app.get("/api/overview")
def overview() -> dict[str, Any]:
    data = store.load_overview()
    data["banner"] = store.dataset_banner()
    data["demo_available"] = store.demo_available()
    quality = store.load_quality()
    data["quality"] = quality
    return data


@app.get("/api/opportunities")
def opportunities(sort: str = Query("rank")) -> list[dict[str, Any]]:
    rows = store.load_opportunities()
    key = sort.lstrip("-")
    if key in {"rank", "frequency", "purchase_association", "evidence_strength", "composite_score", "frequency_percentage"}:
        rows = sorted(
            rows,
            key=lambda r: r.get(key) or 0,
            reverse=(sort.startswith("-") or key != "rank"),
        )
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
        for oid in ids[:20]:
            obs = rel_obs.get(oid)
            if not obs:
                continue
            out.append({"observation": obs, "extraction": ext.get(oid)})
        return out

    return {
        "opportunity": match,
        "themes": themes,
        "supporting": pack(match.get("supporting_evidence_ids") or []),
        "counter": pack(match.get("counter_evidence_ids") or []),
        "banner": store.dataset_banner(),
        "scoring_weights": store.load_pipeline().get("weights"),
    }


@app.get("/api/observations")
def observations(
    source: str | None = None,
    q: str | None = None,
    user_intent: str | None = None,
    purchase_outcome: str | None = None,
    barrier: str | None = None,
    theme: str | None = None,
    limit: int = Query(25, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> dict[str, Any]:
    rows = store.load_relevant()
    ext = store.load_extractions()
    clusters = store.load_clusters()
    themes = store.load_themes()
    cluster_to_theme = {t.get("cluster_id"): t for t in themes}

    filtered: list[dict[str, Any]] = []
    for obs in rows:
        e = ext.get(obs["observation_id"]) or {}
        if source and obs.get("source") != source:
            continue
        if user_intent and e.get("user_intent") != user_intent:
            continue
        if purchase_outcome and e.get("purchase_outcome") != purchase_outcome:
            continue
        if barrier and barrier not in (e.get("barriers") or []):
            continue
        cid = clusters.get(obs["observation_id"])
        theme_obj = cluster_to_theme.get(cid)
        if theme:
            if not theme_obj:
                continue
            blob = (theme_obj.get("theme_id") or "") + " " + (theme_obj.get("theme_name") or "")
            if theme.lower() not in blob.lower():
                continue
        if q:
            text = (obs.get("text_original") or "") + " " + (obs.get("title") or "")
            if q.lower() not in text.lower():
                continue
        filtered.append({"observation": obs, "extraction": e, "theme": theme_obj})
    total = len(filtered)
    return {"total": total, "offset": offset, "limit": limit, "results": filtered[offset : offset + limit]}


@app.get("/api/research")
def research(opportunity_id: str | None = None) -> dict[str, Any]:
    opps = store.load_opportunities()
    if not opps:
        raise HTTPException(404, "No opportunities yet")
    match = next((o for o in opps if o["opportunity_id"] == opportunity_id), None) if opportunity_id else opps[0]
    if not match:
        raise HTTPException(404, "Opportunity not found")
    segment = (match.get("user_segment") or [None])[0]
    plan = generate_interview_plan(match, None if segment == "Insufficient evidence." else segment)
    plan["opportunities"] = [{"opportunity_id": o["opportunity_id"], "rank": o["rank"], "title": o["title"]} for o in opps]
    plan["banner"] = store.dataset_banner()
    return plan
