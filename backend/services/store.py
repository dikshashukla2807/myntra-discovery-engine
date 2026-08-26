from __future__ import annotations

from functools import lru_cache
from typing import Any

from backend.utils.io import read_json, read_jsonl
from config import settings


def _p(*parts: str):
    return settings.PROCESSED_DIR.joinpath(*parts)


def load_overview() -> dict[str, Any]:
    return read_json(_p("overview.json"), {}) or {}


def load_quality() -> dict[str, Any]:
    return read_json(_p("quality_report.json"), {}) or {}


def load_pipeline() -> dict[str, Any]:
    return read_json(_p("pipeline_status.json"), {}) or {}


def load_themes() -> list[dict[str, Any]]:
    return read_json(_p("themes.json"), []) or []


def load_opportunities() -> list[dict[str, Any]]:
    return read_json(_p("opportunities.json"), []) or []


def load_segments() -> list[dict[str, Any]]:
    return read_json(_p("segments.json"), []) or []


def load_gaps() -> list[dict[str, Any]]:
    return read_json(_p("gaps.json"), []) or []


def load_report() -> dict[str, Any]:
    return read_json(_p("discovery_report.json"), {}) or {}


def load_interview() -> dict[str, Any]:
    return read_json(_p("interview_plan.json"), {}) or {}


def load_relevant() -> list[dict[str, Any]]:
    return read_jsonl(settings.PROCESSED_DIR / "relevant_observations.jsonl")


def load_extractions() -> dict[str, dict[str, Any]]:
    rows = read_jsonl(settings.PROCESSED_DIR / "extractions.jsonl")
    return {r["observation_id"]: r for r in rows}


def load_relevance() -> dict[str, dict[str, Any]]:
    rows = read_jsonl(settings.PROCESSED_DIR / "relevance.jsonl")
    return {r["observation_id"]: r for r in rows}


def load_exclusions() -> list[dict[str, Any]]:
    return read_jsonl(settings.PROCESSED_DIR / "exclusions.jsonl")


def load_clusters() -> dict[str, int]:
    rows = read_json(_p("clusters.json"), []) or []
    return {r["observation_id"]: r["cluster_id"] for r in rows if "observation_id" in r}


def dataset_banner() -> dict[str, str]:
    status = load_pipeline()
    label = status.get("dataset_label") or "unknown"
    if label == "demo_sample":
        return {
            "mode": "demo",
            "label": "Demo / Sample Data",
            "detail": "These observations are labeled sample data. They are not real user research and must not be presented as public-source findings.",
        }
    if label == "mixed_public_and_demo":
        return {
            "mode": "mixed",
            "label": "Mixed dataset",
            "detail": "Public-source records and demo/sample records are both present. Filter by dataset_label before quoting evidence.",
        }
    return {
        "mode": "public",
        "label": "Public-source dataset",
        "detail": "Public user-generated content collected from source platforms. Not independently verified as genuine.",
    }
