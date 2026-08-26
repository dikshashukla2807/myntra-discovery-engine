"""YouTube public comment collector.

If YOUTUBE_API_KEY is set, uses the official YouTube Data API v3.
Otherwise collection is a no-op besides recording the gap; use CSV/JSON import.
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
from config.queries import YOUTUBE_SEARCH_TOPICS


def _comment_url(video_id: str, comment_id: str) -> str:
    return f"https://www.youtube.com/watch?v={video_id}&lc={comment_id}"


def _search_videos(client: httpx.Client, api_key: str, query: str, max_results: int = 8) -> list[dict[str, Any]]:
    url = (
        "https://www.googleapis.com/youtube/v3/search"
        f"?part=snippet&type=video&maxResults={max_results}&q={quote_plus(query)}&key={api_key}"
    )

    def _call() -> dict[str, Any]:
        response = client.get(url, timeout=30.0)
        response.raise_for_status()
        return response.json()

    payload = retry(_call)
    return payload.get("items") or []


def _list_comments(client: httpx.Client, api_key: str, video_id: str, max_results: int = 100) -> list[dict[str, Any]]:
    comments: list[dict[str, Any]] = []
    page_token = ""
    while len(comments) < max_results:
        url = (
            "https://www.googleapis.com/youtube/v3/commentThreads"
            f"?part=snippet&videoId={video_id}&maxResults=100&textFormat=plainText&key={api_key}"
        )
        if page_token:
            url += f"&pageToken={page_token}"

        def _call(u=url) -> dict[str, Any]:
            response = client.get(u, timeout=30.0)
            if response.status_code == 403:
                return {"items": []}
            response.raise_for_status()
            return response.json()

        payload = retry(_call)
        items = payload.get("items") or []
        comments.extend(items)
        page_token = payload.get("nextPageToken") or ""
        if not page_token or not items:
            break
        time.sleep(0.4)
    return comments[:max_results]


def collect_youtube(
    target: int | None = None,
    progress: Callable[[str], None] | None = None,
) -> list[dict[str, Any]]:
    target = target or settings.YOUTUBE_TARGET
    log = progress or (lambda msg: print(msg, flush=True))
    collected_at = utc_now()
    out: list[dict[str, Any]] = []

    if not settings.YOUTUBE_API_KEY:
        write_json(
            settings.RAW_DIR / "youtube" / "collection_meta.json",
            {
                "source": "youtube",
                "target": target,
                "collected": 0,
                "collected_at": collected_at,
                "status": "skipped_no_api_key",
                "note": "YOUTUBE_API_KEY not set. Use scripts/import_youtube.py or POST /api/ingest/youtube. No synthetic comments were created.",
            },
        )
        log("[youtube] skipped — no API key. Import JSON/CSV instead. No records fabricated.")
        return out

    seen: set[str] = set()
    headers = {"User-Agent": "MyntraDiscoveryEngine/1.0"}
    with httpx.Client(headers=headers, follow_redirects=True) as client:
        for topic in YOUTUBE_SEARCH_TOPICS:
            if len(out) >= target:
                break
            log(f"[youtube] search {topic}")
            try:
                videos = _search_videos(client, settings.YOUTUBE_API_KEY, topic, max_results=6)
            except Exception as exc:  # noqa: BLE001
                log(f"[youtube] search failed: {exc}")
                continue
            for video in videos:
                if len(out) >= target:
                    break
                video_id = ((video.get("id") or {}).get("videoId")) or ""
                snippet = video.get("snippet") or {}
                if not video_id:
                    continue
                try:
                    threads = _list_comments(client, settings.YOUTUBE_API_KEY, video_id, max_results=40)
                except Exception as exc:  # noqa: BLE001
                    log(f"[youtube] comments failed for {video_id}: {exc}")
                    continue
                for thread in threads:
                    top = ((thread.get("snippet") or {}).get("topLevelComment") or {}).get("snippet") or {}
                    comment_id = ((thread.get("snippet") or {}).get("topLevelComment") or {}).get("id") or thread.get("id")
                    if not comment_id or comment_id in seen:
                        continue
                    text = top.get("textDisplay") or top.get("textOriginal") or ""
                    if not text.strip():
                        continue
                    seen.add(str(comment_id))
                    out.append(
                        normalize_record(
                            source="youtube",
                            source_id=str(comment_id),
                            source_url=_comment_url(video_id, str(comment_id)),
                            text=text,
                            collected_at=collected_at,
                            date=top.get("publishedAt"),
                            rating=None,
                            title=snippet.get("title"),
                            metadata={
                                "video_id": video_id,
                                "video_title": snippet.get("title"),
                                "channel": snippet.get("channelTitle"),
                                "video_date": snippet.get("publishedAt"),
                                "like_count": top.get("likeCount"),
                                "search_topic": topic,
                            },
                            dataset_label="public_source",
                        )
                    )
                    if len(out) >= target:
                        break
                time.sleep(0.5)

    path = settings.RAW_DIR / "youtube" / "comments.jsonl"
    write_jsonl(path, out)
    write_json(
        settings.RAW_DIR / "youtube" / "collection_meta.json",
        {
            "source": "youtube",
            "target": target,
            "collected": len(out),
            "collected_at": collected_at,
            "path": str(path),
        },
    )
    log(f"[youtube] wrote {len(out)} comments to {path}")
    return out
