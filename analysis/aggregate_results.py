from collections import defaultdict
from pathlib import Path
import csv
import json
import math
from statistics import mean, median, stdev


def _load_jsons(path: str):
    files = sorted(Path(path).glob("*.json"))
    rows = []
    for f in files:
        try:
            rows.append(json.loads(f.read_text()))
        except Exception as e:
            raise ValueError(f"Malformed JSON: {f}: {e}")
    if not rows:
        raise ValueError(f"No run files in {path}")
    return rows


def _write_csv(path, rows, fieldnames):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def aggregate(raw_dir: str = "results/raw_runs", out_dir: str = "results/aggregated"):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    rows = _load_jsons(raw_dir)
    _write_csv(out / "tidy_runs.csv", rows, sorted(rows[0].keys()))

    groups = defaultdict(list)
    for r in rows:
        groups[(r["method"], r["scale"], r["security"])].append(r)

    summary = []
    ci_rows = []
    for (method, scale, security), vals in groups.items():
        lats = [v["latency_mean_ms"] for v in vals]
        thr = [v["throughput_msg_per_sec"] for v in vals]
        p50 = [v["latency_p50_ms"] for v in vals]
        p95 = [v["latency_p95_ms"] for v in vals]
        p99 = [v["latency_p99_ms"] for v in vals]
        std = stdev(lats) if len(lats) > 1 else 0.0
        summary.append({
            "method": method, "scale": scale, "security": security,
            "latency_mean_ms": mean(lats), "latency_std_ms": std, "latency_median_ms": median(lats),
            "throughput_mean": mean(thr), "throughput_std": stdev(thr) if len(thr) > 1 else 0.0,
            "error_rate_mean": mean([v["error_rate"] for v in vals]),
            "p50": mean(p50), "p95": mean(p95), "p99": mean(p99), "runs": len(vals),
        })
        se = (std / math.sqrt(len(lats))) if lats else 0.0
        mu = mean(lats)
        ci_rows.append({"method": method, "scale": scale, "security": security, "mean": mu, "std": std, "count": len(lats), "ci95_low": mu - 1.96 * se, "ci95_high": mu + 1.96 * se})

    _write_csv(out / "summary.csv", summary, list(summary[0].keys()))
    _write_csv(out / "confidence_intervals.csv", ci_rows, list(ci_rows[0].keys()))
    return rows, summary, ci_rows
