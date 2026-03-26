from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class StrategyResult:
    success: bool
    latency_ms: float
    throughput_msg_per_sec: float
    timeout: bool = False
    invalid_mapping: bool = False
    semantic_resolution: bool = True
    recovery_time_ms: float = 0.0
    degraded_mode_supported: bool = False


BASE_PROFILES = {
    "ontology_based": {"lat": 2.4, "thr": 3900.0, "sem": 0.95, "rob": 0.80},
    "direct_translation": {"lat": 1.2, "thr": 5200.0, "sem": 0.72, "rob": 0.66},
    "soa": {"lat": 1.8, "thr": 4600.0, "sem": 0.82, "rob": 0.74},
    "opcua_mediated": {"lat": 2.0, "thr": 4300.0, "sem": 0.78, "rob": 0.83},
}
