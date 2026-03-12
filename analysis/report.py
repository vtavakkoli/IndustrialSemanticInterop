"""Generate a transparent benchmark report including claim boundaries."""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def _git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"


def generate_report(results_root: str = "results") -> Path:
    root = Path(results_root)
    summary = json.loads((root / "aggregated" / "summary.json").read_text())

    lines = [
        "# Interoperability Benchmark Report",
        "",
        f"Generated at: {datetime.now(timezone.utc).isoformat()}",
        f"Git commit: {_git_commit()}",
        "",
        "## Run metadata",
        "- Statistics mode: descriptive only.",
        "- Measured and estimated values are separated; this report contains measured values only by default.",
        "",
        "## Results",
    ]
    for row in summary:
        lines.extend([
            f"### {row['scenario_id']} / {row['method']}",
            f"- Runs: {row['runs']}",
            f"- Mean latency (ms): {row['latency_mean_ms']:.4f}",
            f"- Mean throughput (msg/s): {row['throughput_mean_msg_s']:.2f}",
            f"- Validation pass rate: {row['validation_pass_rate']:.3f}",
            f"- Synthetic runs included: {row['synthetic_present']}",
            "",
        ])

    lines.extend([
        "## Limitations",
        "- Protocol adapters are representative bounded implementations and not full standards-compliant stacks.",
        "- OPC UA adapter currently models node-write exchange payloads rather than a live server integration.",
    ])

    out = root / "final_report.md"
    out.write_text("\n".join(lines))
    return out


if __name__ == "__main__":
    generate_report()
