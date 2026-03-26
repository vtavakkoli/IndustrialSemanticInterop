from benchmark.workloads import METHODS, SCALES, SECURITY_MODES, load_scenarios


def test_full_matrix_expansion():
    scenarios = load_scenarios()
    # 5 base scenario files x full cartesian matrix
    assert len(scenarios) == 5 * len(METHODS) * len(SCALES) * len(SECURITY_MODES)

    combos = {(s.method, s.benchmark_parameters["scale"], s.benchmark_parameters["security_mode"]) for s in scenarios}
    assert len(combos) == len(METHODS) * len(SCALES) * len(SECURITY_MODES)


def test_each_scenario_default_repetition_is_100():
    scenarios = load_scenarios()
    assert all(s.benchmark_parameters["repetitions"] == 100 for s in scenarios)
