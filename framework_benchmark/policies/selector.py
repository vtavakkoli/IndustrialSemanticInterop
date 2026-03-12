from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SelectionDecision:
    selected_strategy: str
    policy: str
    reason: str
    scenario_features: dict


class StrategySelector:
    """Rule-based selector extensible for future ML/policy-driven selection."""

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
