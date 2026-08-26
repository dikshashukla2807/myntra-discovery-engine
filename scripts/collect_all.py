#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.scrapers.collect import collect_all  # noqa: E402
from config import settings  # noqa: E402


if __name__ == "__main__":
    settings.ensure_dirs()
    collect_all()
