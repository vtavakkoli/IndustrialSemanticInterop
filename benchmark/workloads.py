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


def load_scenarios(path: str = "scenarios") -> list[ScenarioDefinition]:
    scenarios: list[ScenarioDefinition] = []
    for file in sorted(Path(path).glob("*.json")):
        data = json.loads(file.read_text())
        scenarios.append(ScenarioDefinition(**data))
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
