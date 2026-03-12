"""Structured benchmark metrics models."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class BenchmarkResult:
    scenario_id: str
    method: str
    run_index: int
    seed: int
    repetitions: int
    measured: bool
    synthetic_mode: bool
    success_rate: float
    validation_pass_rate: float
    throughput_msg_per_sec: float
    end_to_end_latency_ms: float
    startup_overhead_ms: float
    payload_bytes: float
    cpu_time_sec: float
    memory_mb_max: float
    # legacy-compatible fields for comprehensive analysis modules
    scale: str
    security: str
    latency_mean_ms: float
    latency_p50_ms: float
    latency_p95_ms: float
    latency_p99_ms: float
    error_rate: float
    failure_rate: float
    cpu_percent_avg: float
    memory_mb_avg: float
    stage_latency_ms: dict[str, float] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
