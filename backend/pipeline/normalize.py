from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from config import settings
from backend.models.schema import Observation
from backend.utils.text import normalize_whitespace, observation_id


def _iso(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    text = str(value).strip()
    return text or None


def normalize_record(
    *,
    source: str,
    source_id: str,
    source_url: str,
    text: str,
    collected_at: str,
    date: Any = None,
    rating: Any = None,
    title: str | None = None,
    metadata: dict[str, Any] | None = None,
    dataset_label: str = "public_source",
) -> dict[str, Any]:
    original = text if text is not None else ""
    rating_value = None
    if rating is not None and rating != "":
        try:
            rating_value = float(rating)
        except (TypeError, ValueError):
            rating_value = None
    obs = Observation(
        observation_id=observation_id(source, str(source_id)),
        source=source,
        source_id=str(source_id),
        source_url=source_url or "",
        date=_iso(date),
        rating=rating_value,
        title=normalize_whitespace(title or "") or None,
        text_original=original,
        text_clean="",
        language=None,
        translated_text=None,
        metadata=metadata or {},
        collected_at=collected_at,
        dataset_label=dataset_label,  # type: ignore[arg-type]
    )
    return obs.model_dump()
