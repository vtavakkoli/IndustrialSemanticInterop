"""Descriptive statistics helpers (no inferential claims)."""

from __future__ import annotations

import json
from pathlib import Path
from statistics import mean, pstdev


def build_descriptive_stats(summary_file: str = "results/aggregated/summary.json") -> Path:
    summary = json.loads(Path(summary_file).read_text())
    rows = []
    for item in summary:
        rows.append({
            "scenario_id": item["scenario_id"],
            "method": item["method"],
            "latency_mean_ms": item["latency_mean_ms"],
            "throughput_mean_msg_s": item["throughput_mean_msg_s"],
            "descriptive_note": "Descriptive statistics only; no inferential significance claims.",
        })

    out = Path(summary_file).parent / "descriptive_stats.json"
    out.write_text(json.dumps({"rows": rows, "aggregate_latency_mean_ms": mean([r["latency_mean_ms"] for r in rows]), "aggregate_latency_std_ms": pstdev([r["latency_mean_ms"] for r in rows]) if len(rows) > 1 else 0.0}, indent=2))
    return out


if __name__ == "__main__":
    build_descriptive_stats()
