from benchmarks.run_trial import run_trial


def test_latency_throughput_sane():
    s = {"scenario_id": "x", "method": "baseline", "workload": "small", "scale": "small", "security": "none"}
    r = run_trial(s, 0, 1)
    assert r["latency_mean_ms"] >= 0
    assert r["throughput_msg_per_sec"] > 0
