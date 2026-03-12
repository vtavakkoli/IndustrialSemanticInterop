from __future__ import annotations

import json
import random
import time
from collections import Counter
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .policies.selector import StrategySelector
from .scenarios.definitions import Scenario, build_scenarios
from .strategies.base import BASE_PROFILES, StrategyResult


FAULT_PENALTIES = {
    "none": (0.0, 0.0),
    "missing_metadata": (0.12, 0.8),
    "ambiguous_mapping": (0.20, 1.0),
    "unit_mismatch": (0.18, 0.6),
    "ontology_service_down": (0.40, 1.2),
    "opcua_endpoint_down": (0.35, 1.1),
    "authentication_failure": (0.30, 1.5),
    "high_load": (0.15, 1.4),
    "secure_and_semantic": (0.22, 1.3),
    "multi_constraint_mixed": (0.27, 1.8),
}


def _simulate_strategy(strategy: str, scenario: Scenario, rng: random.Random) -> StrategyResult:
    p = BASE_PROFILES[strategy]
    failure_bias, latency_bias = FAULT_PENALTIES.get(scenario.fault_mode, (0.0, 0.0))
    security_bias = {"none": 1.0, "auth": 1.05, "encryption": 1.12, "full": 1.18}[scenario.security_mode]
    scale_bias = {"small": 1.0, "medium": 1.1, "large": 1.25}[scenario.scale]

    failure_prob = (1 - p["rob"]) + failure_bias
    if strategy == "ontology_based" and scenario.fault_mode == "ontology_service_down":
        failure_prob += 0.25
    if strategy == "opcua_mediated" and scenario.fault_mode == "opcua_endpoint_down":
        failure_prob += 0.25

    success = rng.random() > min(max(failure_prob, 0.01), 0.95)
    timeout = scenario.fault_mode in {"high_load", "multi_constraint_mixed"} and rng.random() < 0.1
    invalid_mapping = scenario.fault_mode in {"ambiguous_mapping", "unit_mismatch"} and rng.random() < 0.2
    semantic_resolution = rng.random() < p["sem"]

    latency_ms = p["lat"] * security_bias * scale_bias + latency_bias + rng.random() * 0.3
    throughput = p["thr"] / (security_bias * scale_bias) * (0.9 + rng.random() * 0.2)
    recovery_time = (0.0 if success else 4.0 + rng.random() * 4.0)
    return StrategyResult(
        success=success,
        latency_ms=latency_ms,
        throughput_msg_per_sec=throughput,
        timeout=timeout,
        invalid_mapping=invalid_mapping,
        semantic_resolution=semantic_resolution,
        recovery_time_ms=recovery_time,
        degraded_mode_supported=strategy in {"soa", "opcua_mediated", "adaptive_selection"},
    )


def _execute_adaptive(scenario: Scenario, policy: str, selector: StrategySelector, rng: random.Random) -> dict[str, Any]:
    t0 = time.perf_counter()
    decision = selector.select(
        policy=policy,
        scenario_features={
            "latency_sensitivity": scenario.latency_sensitivity,
            "semantic_complexity": scenario.semantic_complexity,
            "security": scenario.security_mode,
            "interoperability_breadth": scenario.interoperability_breadth,
            "fault_mode": scenario.fault_mode,
            "resource_constraints": scenario.resource_constraints,
        },
    )
    selected = _simulate_strategy(decision.selected_strategy, scenario, rng)
    fallback_used = False
    fallback_success = False
    switch_count = 0
    selected_strategy = decision.selected_strategy

    if not selected.success:
        fallback_used = True
        switch_count = 1
        backup = "soa" if decision.selected_strategy != "soa" else "direct_translation"
        fallback = _simulate_strategy(backup, scenario, rng)
        fallback_success = fallback.success
        if fallback.success:
            selected = fallback
            selected_strategy = backup

    policy_overhead = (time.perf_counter() - t0) * 1000.0
    return {
        "selected_strategy": selected_strategy,
        "policy": policy,
        "decision_reason": decision.reason,
        "scenario_features": decision.scenario_features,
        "fallback_used": fallback_used,
        "fallback_success": fallback_success,
        "strategy_switch_count": switch_count,
        "policy_overhead_ms": policy_overhead,
        "result": selected,
    }


def run_campaign(config: dict[str, Any]) -> list[dict[str, Any]]:
    seed = int(config["seed"])
    repetitions = int(config["repetitions"])
    scenarios = build_scenarios(config["scales"], config["security_modes"], config.get("scenario_flags", ["none"]))
    strategies = config["strategies"]
    policies = config.get("policies", ["balanced"])
    selector = StrategySelector()

    records: list[dict[str, Any]] = []
    for scenario in scenarios:
        for run_index in range(repetitions):
            for strategy in strategies:
                rng = random.Random(seed + run_index + hash((scenario.scenario_id, strategy)) % 10000)
                rec: dict[str, Any] = {
                    "scenario_id": scenario.scenario_id,
                    "scale": scenario.scale,
                    "security_mode": scenario.security_mode,
                    "fault_mode": scenario.fault_mode,
                    "run_index": run_index,
                    "seed": seed + run_index,
                    "strategy": strategy,
                    "method": strategy,
                    "security": scenario.security_mode,
                }
                if strategy == "adaptive_selection":
                    policy = policies[run_index % len(policies)]
                    ad = _execute_adaptive(scenario, policy, selector, rng)
                    result = ad.pop("result")
                    rec.update(ad)
                else:
                    result = _simulate_strategy(strategy, scenario, rng)
                    rec.update(
                        {
                            "selected_strategy": strategy,
                            "policy": "fixed",
                            "decision_reason": "fixed strategy run",
                            "scenario_features": asdict(scenario),
                            "fallback_used": False,
                            "fallback_success": False,
                            "strategy_switch_count": 0,
                            "policy_overhead_ms": 0.0,
                        }
                    )

                rec.update(
                    {
                        "latency": result.latency_ms,
                        "latency_mean_ms": result.latency_ms,
                        "latency_p50_ms": result.latency_ms,
                        "latency_p95_ms": result.latency_ms * 1.12,
                        "latency_p99_ms": result.latency_ms * 1.20,
                        "throughput": result.throughput_msg_per_sec,
                        "throughput_msg_per_sec": result.throughput_msg_per_sec,
                        "success": result.success,
                        "failure": not result.success,
                        "failure_rate": 0.0 if result.success else 1.0,
                        "success_rate": 1.0 if result.success else 0.0,
                        "error_rate": 0.0 if result.success else 1.0,
                        "timeout": result.timeout,
                        "recovery_time": result.recovery_time_ms,
                        "degraded_mode_supported": result.degraded_mode_supported,
                        "invalid_mapping": result.invalid_mapping,
                        "semantic_resolution": result.semantic_resolution,
                        "resource_usage_cpu": 0.0,
                        "resource_usage_memory": 0.0,
                        "confidence_score": 0.0,
                        "mapping_validity_score": 1.0 - float(result.invalid_mapping),
                    }
                )
                records.append(rec)
    return records


def write_records(records: list[dict[str, Any]], raw_dir: str) -> None:
    out = Path(raw_dir)
    out.mkdir(parents=True, exist_ok=True)
    for i, rec in enumerate(records):
        (out / f"campaign_{i:06d}.json").write_text(json.dumps(rec, indent=2), encoding="utf-8")


def summarize_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(records)
    success = sum(1 for r in records if r["success"])
    fallback_total = sum(1 for r in records if r["fallback_used"])
    fallback_success = sum(1 for r in records if r["fallback_success"])
    distribution = Counter(r["selected_strategy"] for r in records if r["strategy"] == "adaptive_selection")

    return {
        "total_runs": total,
        "success_rate": success / total if total else 0.0,
        "failure_rate": 1.0 - (success / total if total else 0.0),
        "timeout_rate": sum(1 for r in records if r["timeout"]) / total if total else 0.0,
        "fallback_rate": fallback_total / total if total else 0.0,
        "fallback_success_rate": fallback_success / fallback_total if fallback_total else 0.0,
        "selected_strategy_distribution": dict(distribution),
    }
