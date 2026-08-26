"""Google Play public review collector for Myntra (com.myntra.android).

Uses the google-play-scraper library, which reads publicly listed reviews.
Does not bypass CAPTCHA, authentication, or rate limits.
Does not collect private account data.
"""

from __future__ import annotations

import time
from typing import Any, Callable

from google_play_scraper import Sort, reviews as play_reviews

from backend.pipeline.normalize import normalize_record
from backend.utils.io import utc_now, write_json, write_jsonl
from backend.utils.rate_limit import retry
from config import settings

APP_ID = settings.MYNTRA_PLAY_APP_ID
PLAY_URL = settings.MYNTRA_PLAY_URL


def _review_url(review_id: str) -> str:
    # Play Store deep link used by Google for individual public reviews.
    return f"{PLAY_URL}&reviewId={review_id}"


def _serialize_review(raw: dict[str, Any], collected_at: str) -> dict[str, Any]:
    review_id = str(raw.get("reviewId") or raw.get("review_id") or "")
    reply = raw.get("replyContent")
    return normalize_record(
        source="google_play",
        source_id=review_id,
        source_url=_review_url(review_id) if review_id else PLAY_URL,
        text=raw.get("content") or "",
        collected_at=collected_at,
        date=raw.get("at"),
        rating=raw.get("score"),
        title=None,
        metadata={
            "user_name": raw.get("userName"),
            "helpful_count": raw.get("thumbsUpCount"),
            "app_version": raw.get("reviewCreatedVersion") or raw.get("appVersion"),
            "developer_reply": reply,
            "developer_reply_date": str(raw.get("repliedAt") or "") or None,
            "raw_keys": sorted(raw.keys()),
        },
        dataset_label="public_source",
    )


def collect_google_play(
    target: int | None = None,
    langs: list[tuple[str, str]] | None = None,
    sleep_seconds: float = 1.25,
    progress: Callable[[str], None] | None = None,
) -> list[dict[str, Any]]:
    """Paginate public reviews. Target is a cap, not a fabrication quota."""
    target = target or settings.PLAY_REVIEW_TARGET
    langs = langs or [("en", "in"), ("hi", "in")]
    collected_at = utc_now()
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    log = progress or (lambda msg: print(msg, flush=True))

    per_lang = max(200, target)
    for lang, country in langs:
        if len(out) >= target:
            break
        token = None
        log(f"[google_play] collecting lang={lang} country={country}")
        while len(out) < target:
            remaining = min(200, target - len(out), per_lang)
            token_ref = token

            def _fetch(t=token_ref, n=remaining, lg=lang, ctry=country):
                return play_reviews(
                    APP_ID,
                    lang=lg,
                    country=ctry,
                    sort=Sort.NEWEST,
                    count=n,
                    continuation_token=t,
                )

            batch, token = retry(_fetch, attempts=4, base_delay=2.0)
            if not batch:
                break
            added = 0
            for raw in batch:
                review_id = str(raw.get("reviewId") or "")
                if not review_id or review_id in seen:
                    continue
                seen.add(review_id)
                out.append(_serialize_review(raw, collected_at))
                added += 1
                if len(out) >= target:
                    break
            log(f"[google_play] {len(out)} unique reviews (+{added})")
            if not token or added == 0:
                break
            time.sleep(sleep_seconds)

    raw_path = settings.RAW_DIR / "google_play" / "reviews.jsonl"
    meta_path = settings.RAW_DIR / "google_play" / "collection_meta.json"
    write_jsonl(raw_path, out)
    write_json(
        meta_path,
        {
            "source": "google_play",
            "app_id": APP_ID,
            "target": target,
            "collected": len(out),
            "collected_at": collected_at,
            "path": str(raw_path),
            "note": "Public user-generated content collected from Google Play. Counts are actual, not padded.",
        },
    )
    log(f"[google_play] wrote {len(out)} reviews to {raw_path}")
    return out
