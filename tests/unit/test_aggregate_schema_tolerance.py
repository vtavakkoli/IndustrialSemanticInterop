import json

from analysis.aggregate import aggregate_results


def test_aggregate_accepts_current_and_legacy_schema(tmp_path):
    raw = tmp_path / "raw"
    out = tmp_path / "agg"
    raw.mkdir()

    current = {
        "scenario_id": "s1",
        "method": "direct_adapter",
        "end_to_end_latency_ms": 1.2,
        "throughput_msg_per_sec": 100.0,
        "validation_pass_rate": 1.0,
        "measured": True,
        "synthetic_mode": False,
    }
    legacy = {
        "scenario_id": "s1",
        "method": "direct_adapter",
        "latency_mean_ms": 0.8,
        "throughput_msg_per_sec": 120.0,
        "error_rate": 0.0,
    }

    (raw / "current.json").write_text(json.dumps(current))
    (raw / "legacy.json").write_text(json.dumps(legacy))

    summary_path = aggregate_results(str(raw), str(out))
    rows = json.loads(summary_path.read_text())
    assert len(rows) == 1
    assert rows[0]["scenario_id"] == "s1"
    assert rows[0]["method"] == "direct_adapter"
    assert rows[0]["runs"] == 2
    assert rows[0]["latency_mean_ms"] == 1.0


def test_aggregate_skips_incompatible_artifacts(tmp_path):
    raw = tmp_path / "raw"
    out = tmp_path / "agg"
    raw.mkdir()

    (raw / "bad.json").write_text(json.dumps({"foo": "bar"}))

    summary_path = aggregate_results(str(raw), str(out))
    rows = json.loads(summary_path.read_text())
    assert rows == []
