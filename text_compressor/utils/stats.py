# text_compressor/utils/stats.py
"""Tiny placeholder for Stats & Timer so algorithms can import them.

A fuller implementation with compression‑ratio calculation will be added in
Phase 6 (CLI integration)."""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter


@dataclass
class Stats:
    orig_size: int
    comp_size: int
    ratio: float
    time_sec: float


class Timer:
    """Context-manager timer AND direct timer. Use:
    • with Timer() as t: ...
    • t = Timer(); t.elapsed()"""

    def __init__(self):
        self._start = perf_counter()
        self._end = None

    def elapsed(self) -> float:
        return (self._end or perf_counter()) - self._start

    def __enter__(self) -> "Timer":
        self._start = perf_counter()
        return self

    def __exit__(self, exc_type, exc, tb):
        self._end = perf_counter()
        # Don’t suppress exceptions
        return False
