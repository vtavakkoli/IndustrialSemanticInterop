"""Aggregate benchmark JSON runs into reproducible descriptive summaries."""

from __future__ import annotations

import json
from pathlib import Path
from statistics import mean


def aggregate_results(raw_dir: str = "results/raw_runs", output_dir: str = "results/aggregated") -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    grouped: dict[str, list[dict]] = {}
    for file in sorted(Path(raw_dir).glob("*.json")):
        data = json.loads(file.read_text())
        key = f"{data['scenario_id']}::{data['method']}"
        grouped.setdefault(key, []).append(data)

    summary = []
    for key, rows in grouped.items():
        scenario_id, method = key.split("::")
        summary.append({
            "scenario_id": scenario_id,
            "method": method,
            "runs": len(rows),
            "latency_mean_ms": mean([r["end_to_end_latency_ms"] for r in rows]),
            "throughput_mean_msg_s": mean([r["throughput_msg_per_sec"] for r in rows]),
            "validation_pass_rate": mean([r["validation_pass_rate"] for r in rows]),
            "measured_only": all(r["measured"] for r in rows),
            "synthetic_present": any(r["synthetic_mode"] for r in rows),
            "statistics_mode": "descriptive",
        })

    path = out / "summary.json"
    path.write_text(json.dumps(summary, indent=2))
    return path


if __name__ == "__main__":
    aggregate_results()
