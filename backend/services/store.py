from __future__ import annotations

from typing import Any

from backend.utils.io import read_json, read_jsonl, write_json
from config import settings


def _mode() -> str:
    data = read_json(settings.ACTIVE_MODE_PATH, {"mode": "public"}) or {"mode": "public"}
    mode = data.get("mode") or "public"
    return "demo" if mode == "demo" else "public"


def set_mode(mode: str) -> dict[str, str]:
    mode = "demo" if mode == "demo" else "public"
    write_json(settings.ACTIVE_MODE_PATH, {"mode": mode})
    return dataset_banner()


def processed_dir():
    return settings.PROCESSED_DEMO_DIR if _mode() == "demo" else settings.PROCESSED_PUBLIC_DIR


def _p(*parts: str):
    return processed_dir().joinpath(*parts)


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


def load_gaps() -> list[dict[str, Any]]:
    return read_json(_p("gaps.json"), []) or []


def load_interview() -> dict[str, Any]:
    return read_json(_p("interview_plan.json"), {}) or {}


def load_relevant() -> list[dict[str, Any]]:
    return read_jsonl(processed_dir() / "relevant_observations.jsonl")


def load_extractions() -> dict[str, dict[str, Any]]:
    rows = read_jsonl(processed_dir() / "extractions.jsonl")
    return {r["observation_id"]: r for r in rows}


def load_relevance() -> dict[str, dict[str, Any]]:
    rows = read_jsonl(processed_dir() / "relevance.jsonl")
    return {r["observation_id"]: r for r in rows}


def load_clusters() -> dict[str, int]:
    rows = read_json(_p("clusters.json"), []) or []
    return {r["observation_id"]: r["cluster_id"] for r in rows if "observation_id" in r}


def demo_available() -> bool:
    return (settings.PROCESSED_DEMO_DIR / "overview.json").exists()


def dataset_banner() -> dict[str, str]:
    if _mode() == "demo":
        return {
            "mode": "demo",
            "label": "DEMO / SAMPLE DATA",
            "detail": "These observations are labeled sample data. They are not real user research and must not be presented as public-source findings.",
        }
    return {
        "mode": "public",
        "label": "Public-source dataset",
        "detail": "Public user-generated content collected from source platforms. Not independently verified as genuine.",
    }
