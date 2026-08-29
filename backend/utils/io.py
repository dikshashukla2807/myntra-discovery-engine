from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Iterator, Union

PathLike = Union[str, Path]


def _path(path: PathLike) -> Path:
    return path if isinstance(path, Path) else Path(path)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: PathLike, payload: Any) -> None:
    path = _path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")


def read_json(path: PathLike, default: Any = None) -> Any:
    path = _path(path)
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_jsonl(path: PathLike, rows: Iterable[dict[str, Any]]) -> int:
    path = _path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, default=str) + "\n")
            count += 1
    return count


def append_jsonl(path: PathLike, rows: Iterable[dict[str, Any]]) -> int:
    path = _path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("a", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, default=str) + "\n")
            count += 1
    return count


def read_jsonl(path: PathLike) -> list[dict[str, Any]]:
    path = _path(path)
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def iter_jsonl(path: PathLike) -> Iterator[dict[str, Any]]:
    path = _path(path)
    if not path.exists():
        return
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                yield json.loads(line)


def load_jsonl_unique(path: PathLike, id_field: str = "source_id") -> tuple[list[dict[str, Any]], set[str]]:
    """Load existing JSONL without dropping prior public records on a re-collect."""
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in read_jsonl(path):
        sid = str(row.get(id_field) or "")
        if not sid or sid in seen:
            continue
        seen.add(sid)
        rows.append(row)
    return rows, seen


def load_all_jsonl(directory: PathLike) -> list[dict[str, Any]]:
    directory = _path(directory)
    rows: list[dict[str, Any]] = []
    if not directory.exists():
        return rows
    for path in sorted(directory.glob("*.jsonl")):
        rows.extend(read_jsonl(path))
    return rows
