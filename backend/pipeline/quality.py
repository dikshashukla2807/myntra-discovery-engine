from __future__ import annotations

from typing import Any

from backend.ai.heuristics import detect_spam_or_low_value
from backend.utils.text import collapse_repeats, content_hash, is_mostly_symbols, normalize_whitespace

try:
    from langdetect import detect, LangDetectException
except Exception:  # pragma: no cover
    detect = None
    LangDetectException = Exception


def clean_observation(obs: dict[str, Any]) -> dict[str, Any]:
    original = obs.get("text_original") or ""
    cleaned = collapse_repeats(normalize_whitespace(original))
    obs = dict(obs)
    obs["text_clean"] = cleaned
    # Never overwrite text_original
    obs["text_original"] = original
    return obs


def detect_language(obs: dict[str, Any]) -> dict[str, Any]:
    obs = dict(obs)
    text = obs.get("text_clean") or obs.get("text_original") or ""
    if not text or detect is None:
        obs["language"] = obs.get("language") or "unknown"
        return obs
    try:
        obs["language"] = detect(text)
    except LangDetectException:
        obs["language"] = "unknown"
    return obs


def empty_reason(obs: dict[str, Any]) -> str | None:
    text = (obs.get("text_original") or "").strip()
    if not text:
        return "empty"
    if is_mostly_symbols(text):
        return "empty"
    return None


def quality_gate(obs: dict[str, Any], seen_hashes: dict[str, str]) -> tuple[str, str | None]:
    """Return (status, reason). status is included|excluded."""
    empty = empty_reason(obs)
    if empty:
        return "excluded", empty
    digest = content_hash(obs.get("text_original") or "")
    if digest in seen_hashes:
        return "excluded", "duplicate"
    seen_hashes[digest] = obs["observation_id"]
    spam = detect_spam_or_low_value(obs.get("text_original") or "")
    if spam:
        return "excluded", spam
    return "included", None


def source_duplicate_key(obs: dict[str, Any]) -> str:
    return f"{obs.get('source')}:{obs.get('source_id')}"
