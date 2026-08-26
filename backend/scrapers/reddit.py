"""Reddit public post/comment collector.

Live Reddit JSON is often blocked from datacenter IPs (403).
This collector uses the public Arctic Shift archive API, which indexes
public Reddit posts/comments and returns original permalinks and text.
"""

from __future__ import annotations

import time
from typing import Any, Callable
from urllib.parse import quote_plus

import httpx

from backend.pipeline.normalize import normalize_record
from backend.utils.io import utc_now, write_json, write_jsonl
from backend.utils.rate_limit import retry
from config import settings
from config.queries import REDDIT_QUERY_CATEGORIES

SUBREDDITS = [
    "india",
    "AskIndia",
    "IndianFashionAddicts",
    "IndiaSpeaks",
]

# Broad public-archive queries. Full category list is still stored on each record
# when the query text matches a category.
ARCHIVE_QUERIES = [
    ("myntra_broad", "myntra"),
    ("myntra_wishlist", "myntra wishlist"),
    ("myntra_fit", "myntra fit"),
    ("myntra_quality", "myntra quality"),
    ("myntra_return", "myntra return"),
    ("online_fashion", "online shopping clothes"),
]


def _permalink_url(permalink: str, subreddit: str | None = None, post_id: str | None = None) -> str:
    if permalink:
        if permalink.startswith("http"):
            return permalink
        return "https://www.reddit.com" + permalink
    if subreddit and post_id:
        return f"https://www.reddit.com/r/{subreddit}/comments/{post_id}/"
    return "https://www.reddit.com"


def _serialize(data: dict[str, Any], collected_at: str, query: str, category: str, kind: str) -> dict[str, Any] | None:
    post_id = str(data.get("name") or data.get("id") or "")
    if not post_id:
        return None
    title = data.get("title") or ""
    body = data.get("selftext") or data.get("body") or ""
    text = "\n\n".join(part for part in (title, body) if part).strip()
    if not text:
        return None
    created = data.get("created_utc")
    date = None
    if created:
        try:
            date = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(float(created)))
        except (TypeError, ValueError, OSError):
            date = None
    permalink = data.get("permalink") or ""
    subreddit = data.get("subreddit")
    if not permalink and subreddit:
        pid = str(data.get("id") or "").replace("t3_", "").replace("t1_", "")
        link = str(data.get("link_id") or "").replace("t3_", "")
        if kind == "t1" and link:
            permalink = f"/r/{subreddit}/comments/{link}/_/{pid}/"
        elif pid:
            permalink = f"/r/{subreddit}/comments/{pid}/"
    return normalize_record(
        source="reddit",
        source_id=post_id if str(post_id).startswith("t") else f"{kind}_{post_id}",
        source_url=_permalink_url(permalink, subreddit, str(data.get("id") or "")),
        text=text,
        collected_at=collected_at,
        date=date,
        rating=None,
        title=title or None,
        metadata={
            "subreddit": subreddit,
            "score": data.get("score"),
            "upvote_ratio": data.get("upvote_ratio"),
            "kind": kind,
            "query": query,
            "query_category": category,
            "parent_id": data.get("parent_id"),
            "link_id": data.get("link_id"),
            "is_comment": kind == "t1" or bool(data.get("body") and not data.get("title")),
            "num_comments": data.get("num_comments"),
            "collection_method": "arctic_shift_archive",
        },
        dataset_label="public_source",
    )


def _arctic_get(client: httpx.Client, url: str) -> list[dict[str, Any]]:
    def _call() -> dict[str, Any]:
        response = client.get(url, timeout=45.0)
        if response.status_code in {404, 422}:
            return {"data": []}
        if response.status_code == 429:
            time.sleep(5)
            response = client.get(url, timeout=45.0)
        response.raise_for_status()
        return response.json()

    payload = retry(_call, attempts=3, base_delay=2.5)
    data = payload.get("data")
    if isinstance(data, list):
        return data
    return []


def collect_reddit(
    target: int | None = None,
    sleep_seconds: float = 0.6,
    progress: Callable[[str], None] | None = None,
) -> list[dict[str, Any]]:
    target = target or settings.REDDIT_TARGET
    collected_at = utc_now()
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    log = progress or (lambda msg: print(msg, flush=True))
    headers = {"User-Agent": "MyntraDiscoveryEngine/1.0 (academic research; public archive)"}

    with httpx.Client(headers=headers, follow_redirects=True) as client:
        for spec in ARCHIVE_QUERIES:
            if len(out) >= target:
                break
            category, query = spec
            for subreddit in SUBREDDITS:
                if len(out) >= target:
                    break
                kinds = [("t3", "posts/search", f"query={quote_plus(query)}")]
                for kind, path, param in kinds:
                    if len(out) >= target:
                        break
                    url = f"https://arctic-shift.photon-reddit.com/api/{path}?subreddit={quote_plus(subreddit)}&{param}"
                    if "limit=" not in param:
                        url += "&limit=100"
                    log(f"[reddit] archive r/{subreddit} {category} {kind}")
                    try:
                        rows = _arctic_get(client, url)
                    except Exception as exc:  # noqa: BLE001
                        log(f"[reddit] skip {subreddit}/{category}: {exc}")
                        time.sleep(sleep_seconds)
                        continue
                    added = 0
                    for data in rows:
                        if not isinstance(data, dict):
                            continue
                        parsed = _serialize(data, collected_at, query, category, kind)
                        if not parsed or parsed["source_id"] in seen:
                            continue
                        seen.add(parsed["source_id"])
                        out.append(parsed)
                        added += 1
                        if len(out) >= target:
                            break
                    log(f"[reddit] {len(out)} unique (+{added})")
                    time.sleep(sleep_seconds)

        # If still short of target, run leftover original query strings in r/india only.
        if len(out) < min(target, 150):
            for spec in REDDIT_QUERY_CATEGORIES[:8]:
                if len(out) >= target:
                    break
                url = (
                    "https://arctic-shift.photon-reddit.com/api/comments/search"
                    f"?subreddit=india&body={quote_plus(spec['query'])}&limit=50"
                )
                log(f"[reddit] extra {spec['category']}")
                try:
                    rows = _arctic_get(client, url)
                except Exception as exc:  # noqa: BLE001
                    log(f"[reddit] extra skip: {exc}")
                    continue
                for data in rows:
                    parsed = _serialize(data, collected_at, spec["query"], spec["category"], "t1")
                    if not parsed or parsed["source_id"] in seen:
                        continue
                    seen.add(parsed["source_id"])
                    out.append(parsed)
                    if len(out) >= target:
                        break
                time.sleep(sleep_seconds)

    path = settings.RAW_DIR / "reddit" / "observations.jsonl"
    write_jsonl(path, out)
    write_json(
        settings.RAW_DIR / "reddit" / "collection_meta.json",
        {
            "source": "reddit",
            "target": target,
            "collected": len(out),
            "collected_at": collected_at,
            "query_categories": [s["category"] for s in REDDIT_QUERY_CATEGORIES],
            "archive_queries": [q[0] for q in ARCHIVE_QUERIES],
            "subreddits": SUBREDDITS,
            "path": str(path),
            "collection_method": "arctic_shift_public_archive",
            "note": "Live Reddit search JSON was blocked (403). Public Arctic Shift archive used. Actual count may be below target. No records fabricated.",
        },
    )
    log(f"[reddit] wrote {len(out)} observations to {path}")
    return out
