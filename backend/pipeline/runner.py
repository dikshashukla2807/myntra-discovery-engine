from __future__ import annotations

from collections import Counter
from typing import Any

from backend.analytics.gaps import build_gaps
from backend.analytics.interviews import generate_interview_plan
from backend.analytics.report import build_report, html_report
from backend.analytics.segments import discover_segments
from backend.pipeline.discover import (
    build_embeddings,
    build_themes,
    cluster_embeddings,
    extraction_for,
    relevance_for,
    score_opportunities,
)
from backend.pipeline.quality import clean_observation, detect_language, quality_gate, source_duplicate_key
from backend.utils.io import load_all_jsonl, read_jsonl, utc_now, write_json, write_jsonl
from config import settings
from config.taxonomies import OPPORTUNITY_WEIGHTS


STAGE_ORDER = [
    "collection",
    "validation",
    "cleaning",
    "language",
    "duplicates",
    "spam",
    "relevance",
    "extraction",
    "embeddings",
    "clustering",
    "themes",
    "opportunity_scoring",
]


def _stage(name: str, status: str, processed: int = 0, successful: int = 0, failed: int = 0, error: str | None = None) -> dict[str, Any]:
    return {
        "name": name,
        "status": status,
        "processed": processed,
        "successful": successful,
        "failed": failed,
        "pending": 0,
        "error": error,
        "updated_at": utc_now(),
    }


def load_raw_observations(include_demo: bool = False, demo_only: bool = False) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not demo_only:
        for source in ("google_play", "app_store", "reddit", "youtube"):
            rows.extend(load_all_jsonl(settings.RAW_DIR / source))
    if include_demo or demo_only:
        rows.extend(read_jsonl(settings.FIXTURES_DIR / "demo_observations.jsonl"))
    return rows


def run_pipeline(
    *,
    include_demo: bool = False,
    demo_only: bool = False,
    sample_size: int | None = None,
    cluster_count: int | None = None,
    progress=None,
) -> dict[str, Any]:
    settings.ensure_dirs()
    log = progress or (lambda msg: print(msg, flush=True))
    stages: list[dict[str, Any]] = []
    started = utc_now()

    raw = load_raw_observations(include_demo=include_demo, demo_only=demo_only)
    stages.append(_stage("collection", "ok", len(raw), len(raw)))
    sample_size = sample_size if sample_size is not None else settings.SAMPLE_SIZE
    if sample_size and sample_size > 0:
        raw = raw[:sample_size]

    # Validation + source-id dedupe
    seen_ids: set[str] = set()
    validated: list[dict[str, Any]] = []
    exclusions: list[dict[str, Any]] = []
    for obs in raw:
        oid = obs.get("observation_id")
        if not oid:
            exclusions.append({"observation_id": "", "status": "excluded", "reason": "empty", "stage": "validation", "notes": "missing observation_id"})
            continue
        key = source_duplicate_key(obs)
        if key in seen_ids:
            exclusions.append({"observation_id": oid, "status": "excluded", "reason": "duplicate", "stage": "validation", "notes": "duplicate source_id"})
            continue
        seen_ids.add(key)
        validated.append(obs)
    stages.append(_stage("validation", "ok", len(raw), len(validated), len(raw) - len(validated)))

    cleaned = [clean_observation(o) for o in validated]
    write_jsonl(settings.CLEAN_DIR / "observations.jsonl", cleaned)
    stages.append(_stage("cleaning", "ok", len(cleaned), len(cleaned)))

    languaged = [detect_language(o) for o in cleaned]
    stages.append(_stage("language", "ok", len(languaged), len(languaged)))

    seen_hashes: dict[str, str] = {}
    included: list[dict[str, Any]] = []
    for obs in languaged:
        status, reason = quality_gate(obs, seen_hashes)
        if status == "excluded":
            exclusions.append({"observation_id": obs["observation_id"], "status": "excluded", "reason": reason, "stage": "quality"})
        else:
            included.append(obs)
    stages.append(_stage("duplicates", "ok", len(languaged), len(included), len(languaged) - len(included)))
    stages.append(_stage("spam", "ok", len(languaged), len(included), len([e for e in exclusions if e.get("reason") in {"spam", "promotional", "low_information", "bot"}])))

    relevances: list[dict[str, Any]] = []
    relevant_obs: list[dict[str, Any]] = []
    for obs in included:
        rel = relevance_for(obs)
        relevances.append(rel)
        if rel.get("relevant_to_discovery"):
            relevant_obs.append(obs)
        else:
            exclusions.append(
                {
                    "observation_id": obs["observation_id"],
                    "status": "excluded",
                    "reason": "irrelevant",
                    "stage": "relevance",
                    "notes": rel.get("relevance_rationale"),
                }
            )
    write_jsonl(settings.PROCESSED_DIR / "relevance.jsonl", relevances)
    stages.append(_stage("relevance", "ok", len(included), len(relevant_obs), len(included) - len(relevant_obs)))

    extractions: list[dict[str, Any]] = []
    ext_map: dict[str, dict[str, Any]] = {}
    for obs in relevant_obs:
        ext = extraction_for(obs)
        extractions.append(ext)
        ext_map[obs["observation_id"]] = ext
    write_jsonl(settings.PROCESSED_DIR / "extractions.jsonl", extractions)
    stages.append(_stage("extraction", "ok", len(relevant_obs), len(extractions)))

    labels: list[int] = []
    themes: list[dict[str, Any]] = []
    if len(relevant_obs) >= 6:
        texts = [(o.get("text_clean") or o.get("text_original") or "")[:4000] for o in relevant_obs]
        dense, _, _ = build_embeddings(texts)
        k = cluster_count or settings.CLUSTER_COUNT
        labels = cluster_embeddings(dense, k).tolist()
        assignment = [
            {"observation_id": o["observation_id"], "cluster_id": int(labels[i])}
            for i, o in enumerate(relevant_obs)
        ]
        write_json(settings.PROCESSED_DIR / "clusters.json", assignment)
        stages.append(_stage("embeddings", "ok", len(relevant_obs), len(relevant_obs)))
        stages.append(_stage("clustering", "ok", len(relevant_obs), len(relevant_obs)))
        themes = build_themes(relevant_obs, ext_map, labels)
        stages.append(_stage("themes", "ok", len(themes), len(themes)))
    else:
        stages.append(_stage("embeddings", "skipped", 0, 0, error="not enough relevant observations"))
        stages.append(_stage("clustering", "skipped", 0, 0))
        stages.append(_stage("themes", "skipped", 0, 0))

    opportunities = score_opportunities(themes, len(relevant_obs) or 1)
    stages.append(_stage("opportunity_scoring", "ok", len(opportunities), len(opportunities)))
    write_json(settings.PROCESSED_DIR / "themes.json", themes)
    write_json(settings.PROCESSED_DIR / "opportunities.json", opportunities)

    segments = discover_segments(relevant_obs, ext_map, opportunities)
    write_json(settings.PROCESSED_DIR / "segments.json", segments)
    gaps = build_gaps(opportunities)
    write_json(settings.PROCESSED_DIR / "gaps.json", gaps)
    interview = generate_interview_plan(opportunities[0], (opportunities[0].get("user_segment") or [None])[0]) if opportunities else None
    write_json(settings.PROCESSED_DIR / "interview_plan.json", interview or {})

    quality = _quality_report(raw, exclusions, included, relevant_obs, languaged)
    write_json(settings.PROCESSED_DIR / "quality_report.json", quality)
    write_jsonl(settings.PROCESSED_DIR / "exclusions.jsonl", exclusions)
    write_jsonl(settings.CLEAN_DIR / "included.jsonl", included)
    write_jsonl(settings.PROCESSED_DIR / "relevant_observations.jsonl", relevant_obs)

    overview = _overview(raw, included, relevant_obs, ext_map, opportunities, quality)
    write_json(settings.PROCESSED_DIR / "overview.json", overview)

    dataset_label = "demo_sample" if include_demo and all(o.get("dataset_label") == "demo_sample" for o in raw) else "public_source"
    if include_demo and any(o.get("dataset_label") == "demo_sample" for o in raw) and any(o.get("dataset_label") == "public_source" for o in raw):
        dataset_label = "mixed_public_and_demo"
    if all(o.get("dataset_label") == "demo_sample" for o in raw) and raw:
        dataset_label = "demo_sample"
    elif any(o.get("dataset_label") == "public_source" for o in raw):
        dataset_label = "public_source"

    report = build_report(
        quality=quality,
        overview=overview,
        opportunities=opportunities,
        themes=themes,
        segments=segments,
        gaps=gaps,
        interview=interview,
        dataset_label=dataset_label,
    )
    write_json(settings.PROCESSED_DIR / "discovery_report.json", report)
    (settings.PROCESSED_DIR / "discovery_report.html").write_text(html_report(report), encoding="utf-8")

    pipeline_status = {
        "last_run": utc_now(),
        "started_at": started,
        "stages": stages,
        "dataset_label": dataset_label,
        "weights": OPPORTUNITY_WEIGHTS,
        "note": "Each stage writes artifacts under data/. Original text is never overwritten.",
    }
    write_json(settings.PROCESSED_DIR / "pipeline_status.json", pipeline_status)
    log(f"[pipeline] done relevant={len(relevant_obs)} themes={len(themes)} opps={len(opportunities)}")
    return pipeline_status


def _quality_report(raw, exclusions, included, relevant, languaged) -> dict[str, Any]:
    reasons = Counter(e.get("reason") for e in exclusions)
    sources_collected = Counter(o.get("source") for o in raw)
    sources_included = Counter(o.get("source") for o in included)
    sources_relevant = Counter(o.get("source") for o in relevant)
    ratings = Counter(str(int(o["rating"])) for o in raw if o.get("rating") is not None)
    langs = Counter(o.get("language") or "unknown" for o in languaged)
    dates = Counter((o.get("date") or "")[:7] or "unknown" for o in raw)
    return {
        "total_collected": len(raw),
        "duplicates": reasons.get("duplicate", 0),
        "spam": reasons.get("spam", 0) + reasons.get("promotional", 0) + reasons.get("bot", 0),
        "irrelevant": reasons.get("irrelevant", 0),
        "empty": reasons.get("empty", 0),
        "low_information": reasons.get("low_information", 0),
        "valid": len(included),
        "relevant": len(relevant),
        "analyzed": len(relevant),
        "removed": len(exclusions),
        "removal_reasons": dict(reasons),
        "source_distribution": {
            "collected": dict(sources_collected),
            "valid": dict(sources_included),
            "relevant": dict(sources_relevant),
        },
        "rating_distribution": dict(ratings),
        "language_distribution": dict(langs),
        "date_distribution": dict(sorted(dates.items())),
        "disclaimer": "Public user-generated content collected from source platforms. Not independently verified as genuine.",
    }


def _overview(raw, included, relevant, ext_map, opportunities, quality) -> dict[str, Any]:
    wishlist_related = 0
    purchase_related = 0
    intents: Counter[str] = Counter()
    outcomes: Counter[str] = Counter()
    barriers: Counter[str] = Counter()
    workarounds: Counter[str] = Counter()
    external = 0
    for oid, ext in ext_map.items():
        intents[ext.get("user_intent") or "unclear"] += 1
        outcomes[ext.get("purchase_outcome") or "unknown"] += 1
        for b in ext.get("barriers") or []:
            if b not in {"unknown", "other"}:
                barriers[b] += 1
        for w in ext.get("workaround_type") or []:
            workarounds[w] += 1
        if ext.get("wishlist_behavior") not in {None, "no evidence", "unclear"}:
            wishlist_related += 1
        if ext.get("purchase_outcome") in {"purchased", "postponed", "abandoned", "purchased alternative", "still considering"}:
            purchase_related += 1
        if ext.get("external_research"):
            external += 1

    return {
        "funnel": {
            "collected": len(raw),
            "valid": len(included),
            "relevant": len(relevant),
            "purchase_related": purchase_related,
            "wishlist_related": wishlist_related,
        },
        "top_opportunities": opportunities[:5],
        "behavioral": {
            "user_intent": dict(intents),
            "purchase_outcomes": dict(outcomes),
            "why_consider_or_save": dict(Counter(
                r for e in ext_map.values() for r in (e.get("consider_reasons") or []) if r not in {"unclear", "other"}
            )),
            "barriers": dict(barriers.most_common(12)),
            "workarounds": dict(workarounds.most_common(12)),
            "external_research_count": external,
            "external_research_pct": round(100.0 * external / max(len(ext_map), 1), 2),
        },
        "quality": quality,
    }
