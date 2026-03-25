from analysis.adaptive_analysis import summarize_adaptive_vs_static, summarize_scalability


def test_adaptive_vs_static_summary(tmp_path):
    rows = [
        {"scenario_id": "s1", "method": "adaptive_selection", "latency_mean_ms": 1.0, "throughput_msg_per_sec": 100.0, "success_rate": 1.0},
        {"scenario_id": "s1", "method": "direct_translation", "latency_mean_ms": 1.4, "throughput_msg_per_sec": 95.0, "success_rate": 0.9},
    ]
    out = summarize_adaptive_vs_static(rows, str(tmp_path))
    assert out
    assert (tmp_path / "adaptive_vs_static.csv").exists()


def test_scalability_summary(tmp_path):
    rows = [
        {"method": "adaptive_selection", "scale": "small", "offered_load_msg_per_sec": 100.0, "latency_mean_ms": 1.2, "throughput_msg_per_sec": 98.0, "cpu_percent_avg": 20.0, "memory_mb_avg": 120.0},
        {"method": "adaptive_selection", "scale": "large", "offered_load_msg_per_sec": 300.0, "latency_mean_ms": 2.0, "throughput_msg_per_sec": 240.0, "cpu_percent_avg": 65.0, "memory_mb_avg": 420.0},
    ]
    out = summarize_scalability(rows, str(tmp_path))
    assert len(out) == 2
    assert (tmp_path / "scalability_summary.csv").exists()
