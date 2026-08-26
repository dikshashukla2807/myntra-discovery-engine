"""Apple App Store public review collector for Myntra.

Uses the public iTunes Customer Reviews RSS feed (no auth).
If the feed is thinner than the target, the actual count is stored.
CSV/JSON import is supported via backend.scrapers.importer.
"""

from __future__ import annotations

import time
from typing import Any, Callable

import httpx

from backend.pipeline.normalize import normalize_record
from backend.utils.io import utc_now, write_json, write_jsonl
from backend.utils.rate_limit import retry
from config import settings

APP_ID = settings.MYNTRA_APP_STORE_ID
APP_URL = settings.MYNTRA_APP_STORE_URL
RSS_TEMPLATE = (
    "https://itunes.apple.com/{country}/rss/customerreviews/page={page}"
    "/id={app_id}/sortby={sort}/json"
)


def _text(node: Any) -> str:
    if node is None:
        return ""
    if isinstance(node, str):
        return node
    if isinstance(node, dict):
        return str(node.get("label") or node.get("href") or "")
    return str(node)


def _parse_entry(entry: dict[str, Any], collected_at: str, country: str) -> dict[str, Any] | None:
    if "im:rating" not in entry and "rating" not in str(entry).lower():
        # The first RSS entry is often the app metadata, not a review.
        if not entry.get("im:rating"):
            return None
    review_id = _text(entry.get("id"))
    if not review_id:
        return None
    title = _text(entry.get("title"))
    body = _text(entry.get("content"))
    rating_raw = _text(entry.get("im:rating"))
    version = _text(entry.get("im:version"))
    updated = _text(entry.get("updated") or entry.get("im:releaseDate"))
    author = _text((entry.get("author") or {}).get("name") if isinstance(entry.get("author"), dict) else "")
    return normalize_record(
        source="app_store",
        source_id=review_id,
        source_url=APP_URL,
        text=body,
        collected_at=collected_at,
        date=updated,
        rating=rating_raw,
        title=title,
        metadata={
            "app_version": version or None,
            "author": author or None,
            "country": country,
            "feed": "itunes_customer_reviews_rss",
        },
        dataset_label="public_source",
    )


def _fetch_page(country: str, page: int, sort: str, client: httpx.Client) -> dict[str, Any]:
    url = RSS_TEMPLATE.format(country=country, page=page, app_id=APP_ID, sort=sort)

    def _call() -> dict[str, Any]:
        response = client.get(url, timeout=30.0)
        if response.status_code == 404:
            return {}
        response.raise_for_status()
        return response.json()

    return retry(_call, attempts=4, base_delay=1.5)


def collect_app_store(
    target: int | None = None,
    countries: list[str] | None = None,
    max_pages: int = 10,
    sleep_seconds: float = 0.8,
    progress: Callable[[str], None] | None = None,
) -> list[dict[str, Any]]:
    target = target or settings.APP_STORE_REVIEW_TARGET
    # Myntra is an India-focused app; IN is the authentic market.
    # Additional storefronts are tried only to recover more public reviews of the same app.
    countries = countries or ["in"]
    sorts = ["mostrecent", "mosthelpful"]
    collected_at = utc_now()
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    log = progress or (lambda msg: print(msg, flush=True))

    headers = {"User-Agent": "MyntraDiscoveryEngine/1.0 (academic product research)"}
    with httpx.Client(headers=headers, follow_redirects=True) as client:
        for country in countries:
            for sort in sorts:
                if len(out) >= target:
                    break
                for page in range(1, max_pages + 1):
                    if len(out) >= target:
                        break
                    log(f"[app_store] {country} sort={sort} page={page}")
                    payload = _fetch_page(country, page, sort, client)
                    feed = payload.get("feed") or {}
                    entries = feed.get("entry") or []
                    if isinstance(entries, dict):
                        entries = [entries]
                    added = 0
                    for entry in entries:
                        parsed = _parse_entry(entry, collected_at, country)
                        if not parsed:
                            continue
                        if parsed["source_id"] in seen:
                            continue
                        seen.add(parsed["source_id"])
                        out.append(parsed)
                        added += 1
                        if len(out) >= target:
                            break
                    log(f"[app_store] {len(out)} unique reviews (+{added})")
                    if added == 0:
                        break
                    time.sleep(sleep_seconds)

    path = settings.RAW_DIR / "app_store" / "reviews.jsonl"
    write_jsonl(path, out)
    write_json(
        settings.RAW_DIR / "app_store" / "collection_meta.json",
        {
            "source": "app_store",
            "app_id": APP_ID,
            "target": target,
            "collected": len(out),
            "collected_at": collected_at,
            "path": str(path),
            "note": "Public iTunes Customer Reviews RSS. Individual review permalinks are not provided by the feed; source_url is the public app page.",
        },
    )
    log(f"[app_store] wrote {len(out)} reviews to {path}")
    return out
