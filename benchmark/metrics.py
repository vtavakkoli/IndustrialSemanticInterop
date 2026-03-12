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
    stage_latency_ms: dict[str, float] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
