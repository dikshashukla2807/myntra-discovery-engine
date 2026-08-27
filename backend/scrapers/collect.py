from __future__ import annotations

from typing import Callable

from backend.scrapers.app_store import collect_app_store
from backend.scrapers.google_play import collect_google_play
from backend.scrapers.reddit import collect_reddit
from backend.scrapers.youtube import collect_youtube
from backend.utils.io import utc_now, write_json
from config import settings


def collect_all(progress: Callable[[str], None] | None = None, include_app_store: bool = False) -> dict:
    settings.ensure_dirs()
    log = progress or (lambda msg: print(msg, flush=True))
    play = collect_google_play(progress=log)
    store_rows: list = []
    if include_app_store:
        store_rows = collect_app_store(progress=log)
    else:
        log("[app_store] skipped in default workflow (optional collector still exists).")
    reddit = collect_reddit(progress=log)
    youtube = collect_youtube(progress=log)
    summary = {
        "collected_at": utc_now(),
        "targets": {
            "google_play": settings.PLAY_REVIEW_TARGET,
            "reddit": settings.REDDIT_TARGET,
            "youtube": settings.YOUTUBE_TARGET,
        },
        "actual": {
            "google_play": len(play),
            "reddit": len(reddit),
            "youtube": len(youtube),
            "app_store": len(store_rows),
        },
        "total": len(play) + len(store_rows) + len(reddit) + len(youtube),
        "note": "Targets are caps. Missing records were not fabricated. App Store is optional.",
    }
    write_json(settings.RAW_DIR / "collection_summary.json", summary)
    log(f"[collect] done — {summary['actual']} (total {summary['total']})")
    return summary
