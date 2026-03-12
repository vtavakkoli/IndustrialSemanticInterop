from framework_benchmark.reporting.tables import benchmark_campaign_summary
from framework_benchmark.scenarios.definitions import build_scenarios


def test_scenario_builder_respects_flags():
    scenarios = build_scenarios(["small"], ["none"], ["missing_metadata", "high_load"])
    assert len(scenarios) == 2
    assert {s.fault_mode for s in scenarios} == {"missing_metadata", "high_load"}


def test_table_generation_smoke():
    rows = [{"strategy": "adaptive_selection", "scale": "small", "security_mode": "none", "fault_mode": "none", "success": True}]
    table = benchmark_campaign_summary(rows)
    assert table[0]["successful_runs"] == 1
