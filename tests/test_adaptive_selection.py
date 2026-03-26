from framework_benchmark.policies.selector import StrategySelector
from framework_benchmark.runner import _execute_adaptive
from framework_benchmark.scenarios.definitions import Scenario
import random


def test_selector_latency_policy_prefers_direct_translation():
    selector = StrategySelector()
    decision = selector.select("latency_first", {"latency_sensitivity": 0.9, "semantic_complexity": 0.2, "security": "none", "fault_mode": "none", "interoperability_breadth": 0.2, "resource_constraints": 0.1})
    assert decision.selected_strategy == "direct_translation"


def test_adaptive_fallback_keys_present():
    selector = StrategySelector()
    scenario = Scenario("s", "large", "full", "multi_constraint_mixed", 0.9, 0.7, 0.8, 0.9)
    result = _execute_adaptive(scenario, "fault_resilient", selector, random.Random(4))
    assert "fallback_used" in result
    assert "selected_strategy" in result


def test_selector_adaptive_auto_prefers_security_aware_option():
    selector = StrategySelector()
    decision = selector.select(
        "adaptive_auto",
        {
            "latency_sensitivity": 0.4,
            "semantic_complexity": 0.5,
            "security": "full",
            "fault_mode": "none",
            "interoperability_breadth": 0.4,
            "resource_constraints": 0.3,
        },
    )
    assert decision.selected_strategy in {"opcua_mediated", "soa"}
