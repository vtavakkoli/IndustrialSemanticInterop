from __future__ import annotations

from dataclasses import dataclass
from itertools import product


SCENARIO_FLAGS = [
    "missing_metadata",
    "ambiguous_mapping",
    "unit_mismatch",
    "ontology_service_down",
    "opcua_endpoint_down",
    "authentication_failure",
    "high_load",
    "secure_and_semantic",
    "multi_constraint_mixed",
]


@dataclass(slots=True)
class Scenario:
    scenario_id: str
    scale: str
    security_mode: str
    fault_mode: str
    latency_sensitivity: float
    semantic_complexity: float
    interoperability_breadth: float
    resource_constraints: float


def build_scenarios(scales: list[str], security_modes: list[str], scenario_flags: list[str]) -> list[Scenario]:
    scenarios: list[Scenario] = []
    flags = scenario_flags or ["none"]
    for scale, security, fault in product(scales, security_modes, flags):
        lat = 0.4 if scale == "small" else 0.7 if scale == "medium" else 0.9
        sem = 0.9 if fault in {"missing_metadata", "ambiguous_mapping", "secure_and_semantic"} else 0.5
        breadth = 0.9 if fault in {"multi_constraint_mixed", "secure_and_semantic"} else 0.5
        resource = 0.8 if scale == "large" or fault == "high_load" else 0.4
        scenarios.append(
            Scenario(
                scenario_id=f"{scale}__{security}__{fault}",
                scale=scale,
                security_mode=security,
                fault_mode=fault,
                latency_sensitivity=lat,
                semantic_complexity=sem,
                interoperability_breadth=breadth,
                resource_constraints=resource,
            )
        )
    return scenarios
