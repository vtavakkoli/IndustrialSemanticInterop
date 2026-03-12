"""Publication-friendly figure generation for benchmark summaries."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt


def plot_latency(summary_file: str = "results/aggregated/summary.json", output_dir: str = "results/figures") -> Path:
    summary = json.loads(Path(summary_file).read_text())
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    labels = [f"{row['scenario_id']}\n{row['method']}" for row in summary]
    values = [row["latency_mean_ms"] for row in summary]

    plt.figure(figsize=(10, 4.5))
    plt.bar(labels, values, color="#4C72B0")
    plt.ylabel("End-to-end latency (ms)")
    plt.xlabel("Scenario / Method")
    plt.title("Measured latency by scenario and interoperability method")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()

    out = output / "latency_summary.svg"
    plt.savefig(out, format="svg")
    plt.close()
    return out


if __name__ == "__main__":
    plot_latency()
