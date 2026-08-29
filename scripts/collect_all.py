#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.scrapers.collect import collect_all  # noqa: E402
from config import settings  # noqa: E402


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Collect public Myntra UGC. Targets are caps, not quotas.")
    parser.add_argument("--include-app-store", action="store_true", help="Also collect App Store RSS reviews")
    parser.add_argument("--play-target", type=int, default=None)
    parser.add_argument("--app-store-target", type=int, default=None)
    parser.add_argument("--reddit-target", type=int, default=None)
    args = parser.parse_args()
    settings.ensure_dirs()
    collect_all(
        include_app_store=args.include_app_store,
        play_target=args.play_target,
        app_store_target=args.app_store_target,
        reddit_target=args.reddit_target,
    )
