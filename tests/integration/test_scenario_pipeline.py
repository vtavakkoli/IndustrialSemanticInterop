from benchmark.runner import execute_once
from benchmark.workloads import load_scenarios


def test_execute_simple_scenario():
    scenario = [s for s in load_scenarios() if s.scenario_id == "simple_scalar_sensor"][0]
    result = execute_once(scenario, run_index=0, seed=1)
    assert result.success_rate == 1.0
    assert result.validation_pass_rate == 1.0
    assert result.method == "direct_adapter"
