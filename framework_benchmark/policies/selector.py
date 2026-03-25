from __future__ import annotations

from dataclasses import dataclass

from ..strategies.base import BASE_PROFILES


@dataclass(slots=True)
class SelectionDecision:
    selected_strategy: str
    policy: str
    reason: str
    scenario_features: dict


class StrategySelector:
    """Rule-based selector extensible for future ML/policy-driven selection."""

    @staticmethod
    def _strategy_score(strategy: str, features: dict) -> float:
        profile = BASE_PROFILES[strategy]
        latency_target = max(float(features.get("latency_sensitivity", 0.5)), 0.01)
        semantic_target = float(features.get("semantic_complexity", 0.5))
        interoperability_target = float(features.get("interoperability_breadth", 0.5))
        resource_constraints = float(features.get("resource_constraints", 0.5))
        security = features.get("security", "none")
        fault_mode = features.get("fault_mode", "none")

        latency_component = (1.0 / profile["lat"]) * (0.8 + latency_target)
        throughput_component = (profile["thr"] / 5200.0) * (1.0 - (resource_constraints * 0.2))
        semantic_component = profile["sem"] * (0.6 + semantic_target + (0.25 * interoperability_target))
        reliability_component = profile["rob"] * 1.6

        security_bonus = 0.0
        if security in {"encryption", "full"}:
            security_bonus = 0.25 if strategy in {"opcua_mediated", "soa"} else -0.12
        if security == "auth":
            security_bonus = 0.08 if strategy in {"soa", "direct_translation"} else 0.0

        fault_bonus = 0.0
        if fault_mode == "ontology_service_down" and strategy == "ontology_based":
            fault_bonus -= 0.9
        if fault_mode == "opcua_endpoint_down" and strategy == "opcua_mediated":
            fault_bonus -= 0.9
        if fault_mode in {"high_load", "multi_constraint_mixed"} and strategy in {"soa", "opcua_mediated"}:
            fault_bonus += 0.22

        return latency_component + throughput_component + semantic_component + reliability_component + security_bonus + fault_bonus

    def select(self, policy: str, scenario_features: dict) -> SelectionDecision:
        security = scenario_features.get("security", "none")
        fault = scenario_features.get("fault_mode", "none")
        sem = scenario_features.get("semantic_complexity", 0.5)
        latency_sensitive = scenario_features.get("latency_sensitivity", 0.5)
        interoperability_breadth = scenario_features.get("interoperability_breadth", 0.5)

        if policy == "latency_first":
            pick = "direct_translation"
            reason = "low-latency preference dominates."
        elif policy == "semantics_first":
            pick = "ontology_based"
            reason = "semantic complexity prioritized."
        elif policy == "security_first":
            pick = "opcua_mediated" if security in {"encryption", "full"} else "soa"
            reason = "security policy favors mediated/soa path."
        elif policy == "fault_resilient":
            pick = "opcua_mediated" if fault in {"opcua_endpoint_down", "ontology_service_down"} else "soa"
            reason = "fault-resilient policy selected robust strategy."
        elif policy == "adaptive_auto":
            candidates = ["ontology_based", "direct_translation", "soa", "opcua_mediated"]
            scored = sorted(
                ((self._strategy_score(strategy, scenario_features), strategy) for strategy in candidates),
                reverse=True,
            )
            pick = scored[0][1]
            reason = f"contextual score selected {pick} (score={scored[0][0]:.3f})."
        else:
            if sem > 0.7 or interoperability_breadth > 0.7:
                pick = "ontology_based"
                reason = "balanced policy routed to semantic strength."
            elif latency_sensitive > 0.7:
                pick = "direct_translation"
                reason = "balanced policy routed to latency profile."
            else:
                pick = "soa"
                reason = "balanced policy selected middle-ground strategy."

        return SelectionDecision(
            selected_strategy=pick,
            policy=policy,
            reason=reason,
            scenario_features=dict(scenario_features),
        )
