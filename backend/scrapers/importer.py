"""CSV/JSON import for sources that cannot be collected live (especially YouTube / App Store)."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from backend.pipeline.normalize import normalize_record
from backend.utils.io import utc_now, write_jsonl
from config import settings

REQUIRED = ("source", "source_id", "text")


def _load_rows(path: Path) -> list[dict[str, Any]]:
    if path.suffix.lower() == ".jsonl":
        rows = []
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rows.append(json.loads(line))
        return rows
    if path.suffix.lower() == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, list):
            return payload
        if isinstance(payload, dict) and "observations" in payload:
            return payload["observations"]
        raise ValueError("JSON import must be a list or {observations: []}")
    if path.suffix.lower() == ".csv":
        with path.open(encoding="utf-8", newline="") as handle:
            return list(csv.DictReader(handle))
    raise ValueError(f"Unsupported import format: {path.suffix}")


def import_observations(path: Path, default_source: str | None = None) -> list[dict[str, Any]]:
    collected_at = utc_now()
    raw_rows = _load_rows(path)
    out: list[dict[str, Any]] = []
    for row in raw_rows:
        source = (row.get("source") or default_source or "").strip()
        source_id = str(row.get("source_id") or row.get("review_id") or row.get("comment_id") or "").strip()
        text = row.get("text") or row.get("text_original") or row.get("review_text") or row.get("comment_text") or ""
        if not source or not source_id or not str(text).strip():
            continue
        dataset_label = row.get("dataset_label") or "public_source"
        if dataset_label not in {"public_source", "demo_sample"}:
            dataset_label = "public_source"
        out.append(
            normalize_record(
                source=source,
                source_id=source_id,
                source_url=row.get("source_url") or row.get("url") or "",
                text=str(text),
                collected_at=collected_at,
                date=row.get("date") or row.get("review_date") or row.get("comment_date"),
                rating=row.get("rating"),
                title=row.get("title"),
                metadata={k: v for k, v in row.items() if k not in {"text", "text_original", "review_text", "comment_text"}},
                dataset_label=dataset_label,
            )
        )

    dest_dir = settings.RAW_DIR / (default_source or "import")
    dest_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(dest_dir / "imported.jsonl", out)
    return out
