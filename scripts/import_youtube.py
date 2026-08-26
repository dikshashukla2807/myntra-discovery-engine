#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.scrapers.importer import import_observations  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Import public YouTube comments from CSV/JSON")
    parser.add_argument("path")
    args = parser.parse_args()
    rows = import_observations(Path(args.path), default_source="youtube")
    print(f"imported {len(rows)} youtube observations")


if __name__ == "__main__":
    main()
