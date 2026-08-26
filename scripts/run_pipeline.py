#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.pipeline.runner import run_pipeline  # noqa: E402
from config import settings  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the discovery pipeline")
    parser.add_argument("--demo", action="store_true", help="Include labeled demo fixtures")
    parser.add_argument("--demo-only", action="store_true", help="Run only on demo fixtures")
    parser.add_argument("--sample-size", type=int, default=0)
    args = parser.parse_args()
    settings.ensure_dirs()
    run_pipeline(
        include_demo=args.demo,
        demo_only=args.demo_only,
        sample_size=args.sample_size,
    )


if __name__ == "__main__":
    main()
