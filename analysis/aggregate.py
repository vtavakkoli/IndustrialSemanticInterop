"""Aggregate benchmark JSON runs into reproducible descriptive summaries."""

from __future__ import annotations

import json
from pathlib import Path
from statistics import mean
from typing import Any


def _normalize_run(data: dict[str, Any]) -> dict[str, Any] | None:
    """Normalize run dictionaries across legacy and current schemas.

    Returns None when a run lacks required fields for deterministic aggregation.
    """
    scenario_id = data.get("scenario_id")
    method = data.get("method")
    if not scenario_id or not method:
        return None

    latency = data.get("end_to_end_latency_ms", data.get("latency_mean_ms"))
    throughput = data.get("throughput_msg_per_sec")
    if latency is None or throughput is None:
        return None

    validation = data.get("validation_pass_rate")
    if validation is None:
        if "failure_rate" in data:
            validation = 1.0 - float(data["failure_rate"])
        elif "error_rate" in data:
            validation = 1.0 - float(data["error_rate"])
        else:
            validation = 0.0

    return {
        "scenario_id": str(scenario_id),
        "method": str(method),
        "latency_ms": float(latency),
        "throughput_msg_s": float(throughput),
        "validation_pass_rate": float(validation),
        "measured": bool(data.get("measured", True)),
        "synthetic_mode": bool(data.get("synthetic_mode", False)),
    }


def aggregate_results(raw_dir: str = "results/raw_runs", output_dir: str = "results/aggregated") -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    grouped: dict[str, list[dict[str, Any]]] = {}

    total_files = 0
    skipped = 0

    for file in sorted(Path(raw_dir).glob("*.json")):
        total_files += 1
        data = json.loads(file.read_text())
        normalized = _normalize_run(data)
        if normalized is None:
            skipped += 1
            print(f"[aggregate] skipped incompatible artifact: {file.name}", flush=True)
            continue

        key = f"{normalized['scenario_id']}::{normalized['method']}"
        grouped.setdefault(key, []).append(normalized)

    summary = []
    for key, rows in grouped.items():
        scenario_id, method = key.split("::")
        summary.append(
            {
                "scenario_id": scenario_id,
                "method": method,
                "runs": len(rows),
                "latency_mean_ms": mean([r["latency_ms"] for r in rows]),
                "throughput_mean_msg_s": mean([r["throughput_msg_s"] for r in rows]),
                "validation_pass_rate": mean([r["validation_pass_rate"] for r in rows]),
                "measured_only": all(r["measured"] for r in rows),
                "synthetic_present": any(r["synthetic_mode"] for r in rows),
                "statistics_mode": "descriptive",
            }
        )

    path = out / "summary.json"
    path.write_text(json.dumps(summary, indent=2))
    print(
        f"[aggregate] processed artifacts={total_files} grouped_runs={sum(len(v) for v in grouped.values())} "
        f"skipped={skipped} output={path}",
        flush=True,
    )
    return path


if __name__ == "__main__":
    aggregate_results()
