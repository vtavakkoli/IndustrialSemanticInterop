import json

from analysis.aggregate_results import aggregate


def test_aggregate_handles_mixed_row_schemas(tmp_path):
    raw = tmp_path / "raw"
    out = tmp_path / "agg"
    raw.mkdir()

    old_like = {
        "method": "semantic_mapping",
        "scale": "small",
        "security": "none",
        "latency_mean_ms": 1.0,
        "latency_p50_ms": 0.9,
        "latency_p95_ms": 1.2,
        "latency_p99_ms": 1.4,
        "throughput_msg_per_sec": 1000.0,
        "error_rate": 0.01,
    }
    new_like = {
        "method": "adaptive_selection",
        "strategy": "adaptive_selection",
        "scale": "small",
        "security_mode": "none",
        "latency": 2.0,
        "throughput": 900.0,
        "failure_rate": 0.1,
        "metadata": {"note": "nested field should not crash csv"},
    }

    (raw / "a.json").write_text(json.dumps(old_like), encoding="utf-8")
    (raw / "b.json").write_text(json.dumps(new_like), encoding="utf-8")

    _, summary, _ = aggregate(str(raw), str(out))

    assert (out / "tidy_runs.csv").exists()
    assert summary
    methods = {row["method"] for row in summary}
    assert "semantic_mapping" in methods
    assert "adaptive_selection" in methods
