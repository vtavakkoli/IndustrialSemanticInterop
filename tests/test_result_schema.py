from benchmarks.run_trial import run_trial
from benchmarks.validate_results import validate_result


def test_result_schema_validates():
    s = {"scenario_id": "x", "method": "baseline", "workload": "small", "scale": "small", "security": "none"}
    r = run_trial(s, 0, 42)
    assert validate_result(r)
