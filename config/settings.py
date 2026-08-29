from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
CLEAN_DIR = DATA_DIR / "clean"
PROCESSED_DIR = DATA_DIR / "processed"
PROCESSED_PUBLIC_DIR = DATA_DIR / "processed"
PROCESSED_DEMO_DIR = DATA_DIR / "processed_demo"
ACTIVE_MODE_PATH = DATA_DIR / "active_mode.json"
EXPORTS_DIR = DATA_DIR / "exports"
FIXTURES_DIR = DATA_DIR / "fixtures"
AI_CACHE_DIR = DATA_DIR / "processed" / "ai_cache"

MYNTRA_PLAY_APP_ID = "com.myntra.android"
MYNTRA_APP_STORE_ID = "907394059"
MYNTRA_PLAY_URL = "https://play.google.com/store/apps/details?id=com.myntra.android"
MYNTRA_APP_STORE_URL = "https://apps.apple.com/in/app/myntra-fashion-shopping-app/id907394059"


def _bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


DATASET_MODE = os.getenv("DATASET_MODE", "public").strip().lower()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "").strip()
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "").strip()
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "").strip()
REDDIT_USER_AGENT = os.getenv(
    "REDDIT_USER_AGENT",
    "MyntraDiscoveryEngine/1.0 (academic product research; public JSON)",
)

PLAY_REVIEW_TARGET = _int("PLAY_REVIEW_TARGET", 5500)
APP_STORE_REVIEW_TARGET = _int("APP_STORE_REVIEW_TARGET", 2000)
REDDIT_TARGET = _int("REDDIT_TARGET", 1500)
YOUTUBE_TARGET = _int("YOUTUBE_TARGET", 500)
SAMPLE_SIZE = _int("SAMPLE_SIZE", 0)
FORCE_REPROCESS = _bool("FORCE_REPROCESS", False)
CLUSTER_COUNT = _int("CLUSTER_COUNT", 8)

API_HOST = os.getenv("API_HOST", "127.0.0.1")
API_PORT = _int("API_PORT", 43124)
CORS_ORIGINS = [
    o.strip()
    for o in os.getenv(
        "CORS_ORIGINS", "http://127.0.0.1:43125,http://localhost:43125"
    ).split(",")
    if o.strip()
]


def ensure_dirs() -> None:
    for path in (
        RAW_DIR / "google_play",
        RAW_DIR / "app_store",
        RAW_DIR / "reddit",
        RAW_DIR / "youtube",
        CLEAN_DIR,
        PROCESSED_PUBLIC_DIR,
        PROCESSED_DEMO_DIR,
        EXPORTS_DIR,
        FIXTURES_DIR,
        AI_CACHE_DIR,
    ):
        path.mkdir(parents=True, exist_ok=True)
