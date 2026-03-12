"""Scenario loading and pipeline construction."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from adapters.hybrid_adapter import HybridPipelineAdapter
from adapters.iec61499_adapter import IEC61499StyleAdapter
from adapters.ieee1451_adapter import IEEE1451StyleAdapter
from adapters.opcua_adapter import OPCUABridgeAdapter
from mappings.engine import MappingEngine

METHODS = ["semantic_mapping", "opcua_bridge", "hybrid_pipeline", "direct_adapter"]
SCALES = ["small", "medium", "large"]
SECURITY_MODES = ["none", "auth", "encryption", "full"]


@dataclass(slots=True)
class ScenarioDefinition:
    scenario_id: str
    description: str
    method: str
    source_protocol: str
    target_protocol: str
    payload: dict[str, Any]
    mapping_rules: dict[str, Any]
    expected_output: dict[str, Any]
    validation_criteria: dict[str, Any]
    benchmark_parameters: dict[str, Any]


def _target_protocol_for_method(method: str) -> str:
    if method == "opcua_bridge":
        return "opcua_bridge"
    return "iec61499_style"


def _expected_for_method(payload: dict[str, Any], method: str) -> dict[str, Any]:
    signal_id = payload["transducer_channel"]
    if method == "opcua_bridge":
        return {"node_id": f"ns=2;s={signal_id}"}
    return {"fb_type": "AI_BLOCK", "data": {"id": signal_id}}


def load_scenarios(path: str = "scenarios") -> list[ScenarioDefinition]:
    scenarios: list[ScenarioDefinition] = []
    for file in sorted(Path(path).glob("*.json")):
        base = json.loads(file.read_text())
        for method in METHODS:
            for scale in SCALES:
                for security_mode in SECURITY_MODES:
                    scenario_id = f"{base['scenario_id']}__{method}__{scale}__{security_mode}"
                    benchmark_parameters = dict(base.get("benchmark_parameters", {}))
                    benchmark_parameters["scale"] = scale
                    benchmark_parameters["security_mode"] = security_mode
                    benchmark_parameters["repetitions"] = 100

                    scenarios.append(
                        ScenarioDefinition(
                            scenario_id=scenario_id,
                            description=f"{base['description']} [method={method}, scale={scale}, security={security_mode}]",
                            method=method,
                            source_protocol=base.get("source_protocol", "ieee1451_style"),
                            target_protocol=_target_protocol_for_method(method),
                            payload=base["payload"],
                            mapping_rules=base.get("mapping_rules", {}),
                            expected_output=_expected_for_method(base["payload"], method),
                            validation_criteria=base.get("validation_criteria", {"required_pass_rate": 1.0}),
                            benchmark_parameters=benchmark_parameters,
                        )
                    )
    return scenarios


def build_pipeline(method: str):
    source = IEEE1451StyleAdapter()
    mapping = MappingEngine()
    if method == "direct_adapter":
        target = IEC61499StyleAdapter()
    elif method == "semantic_mapping":
        target = IEC61499StyleAdapter()
    elif method == "opcua_bridge":
        target = OPCUABridgeAdapter()
    elif method == "hybrid_pipeline":
        target = HybridPipelineAdapter()
    else:
        raise ValueError(f"Unsupported method {method}")
    return source, mapping, target
