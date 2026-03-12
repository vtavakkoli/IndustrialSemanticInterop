"""Instrumentation utilities for stage-level timing and resource snapshots."""

from __future__ import annotations

import resource
import time
from contextlib import contextmanager
from dataclasses import dataclass


@dataclass(slots=True)
class ResourceSnapshot:
    cpu_time_sec: float
    max_rss_mb: float


def read_resource_snapshot() -> ResourceSnapshot:
    usage = resource.getrusage(resource.RUSAGE_SELF)
    return ResourceSnapshot(
        cpu_time_sec=usage.ru_utime + usage.ru_stime,
        max_rss_mb=usage.ru_maxrss / 1024.0,
    )


@contextmanager
def stage_timer(stage: str, store: dict[str, float]):
    start = time.perf_counter()
    yield
    store[stage] = (time.perf_counter() - start) * 1000.0
