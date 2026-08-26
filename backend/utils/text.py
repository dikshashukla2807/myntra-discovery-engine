from __future__ import annotations

import hashlib
import re
import unicodedata

WHITESPACE_RE = re.compile(r"\s+")
URL_RE = re.compile(r"https?://\S+", re.I)
REPEAT_CHAR_RE = re.compile(r"(.)\1{6,}")
EMOJI_HEAVY_RE = re.compile(r"[\U0001F300-\U0001FAFF]")


def normalize_whitespace(text: str) -> str:
    return WHITESPACE_RE.sub(" ", (text or "").strip())


def fold_for_hash(text: str) -> str:
    folded = unicodedata.normalize("NFKC", text or "").lower()
    folded = URL_RE.sub(" ", folded)
    folded = normalize_whitespace(folded)
    return folded


def content_hash(text: str) -> str:
    return hashlib.sha256(fold_for_hash(text).encode("utf-8")).hexdigest()


def observation_id(source: str, source_id: str) -> str:
    raw = f"{source}:{source_id}"
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
    return f"{source[:2]}-{digest}"


def token_count(text: str) -> int:
    return len([t for t in re.findall(r"\w+", text or "") if t])


def is_mostly_symbols(text: str) -> bool:
    compact = (text or "").strip()
    if not compact:
        return True
    letters = sum(1 for ch in compact if ch.isalpha())
    return letters / max(len(compact), 1) < 0.2


def collapse_repeats(text: str) -> str:
    return REPEAT_CHAR_RE.sub(r"\1\1\1", text or "")
