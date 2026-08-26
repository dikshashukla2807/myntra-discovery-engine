from __future__ import annotations

import time
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")


class RateLimiter:
    def __init__(self, min_interval_seconds: float) -> None:
        self.min_interval_seconds = min_interval_seconds
        self._last = 0.0

    def wait(self) -> None:
        now = time.monotonic()
        gap = self.min_interval_seconds - (now - self._last)
        if gap > 0:
            time.sleep(gap)
        self._last = time.monotonic()


def retry(fn: Callable[[], T], attempts: int = 4, base_delay: float = 2.0) -> T:
    last_error: Exception | None = None
    for i in range(attempts):
        try:
            return fn()
        except Exception as exc:  # noqa: BLE001 — collectors must survive transient HTTP errors
            last_error = exc
            time.sleep(base_delay * (2**i))
    assert last_error is not None
    raise last_error
