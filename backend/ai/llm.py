"""Optional OpenAI-compatible client. Never used to invent source text."""

from __future__ import annotations

import hashlib
import json
from typing import Any

import httpx

from backend.utils.io import read_json, write_json
from config import settings


def llm_available() -> bool:
    return bool(settings.OPENAI_API_KEY)


def _cache_path(key: str):
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
    return settings.AI_CACHE_DIR / f"{digest}.json"


def complete_json(system: str, user: str, cache_key: str) -> dict[str, Any] | None:
    if not llm_available():
        return None
    settings.AI_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = _cache_path(cache_key)
    if path.exists() and not settings.FORCE_REPROCESS:
        cached = read_json(path)
        if isinstance(cached, dict):
            return cached
    payload = {
        "model": settings.OPENAI_MODEL,
        "temperature": 0,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }
    try:
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                f"{settings.OPENAI_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            parsed = json.loads(content)
    except Exception:
        return None
    write_json(path, parsed)
    return parsed
