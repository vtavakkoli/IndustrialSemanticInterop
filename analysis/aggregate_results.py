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
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, "") for k in fieldnames})


def _as_float(v, default=0.0):
    try:
        return float(v)
    except Exception:
        return default


def _get_metric(row, primary, fallback=None, default=0.0):
    if primary in row:
        return _as_float(row.get(primary), default)
    if fallback and fallback in row:
        return _as_float(row.get(fallback), default)
    return default


def _group_key(row):
    return (
        row.get("method", row.get("strategy", "unknown")),
        row.get("scale", "unknown"),
        row.get("security", row.get("security_mode", "unknown")),
    )


def aggregate(raw_dir: str = "results/raw_runs", out_dir: str = "results/aggregated"):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    rows = _load_jsons(raw_dir)

    all_keys = sorted({k for row in rows for k in row.keys()})
    _write_csv(out / "tidy_runs.csv", rows, all_keys)

    groups = defaultdict(list)
    for r in rows:
        groups[_group_key(r)].append(r)

    summary = []
    ci_rows = []
    for (method, scale, security), vals in groups.items():
        lats = [_get_metric(v, "latency_mean_ms", "latency") for v in vals]
        thr = [_get_metric(v, "throughput_msg_per_sec", "throughput") for v in vals]
        p50 = [_get_metric(v, "latency_p50_ms", "latency_mean_ms") for v in vals]
        p95 = [_get_metric(v, "latency_p95_ms", "latency_mean_ms") for v in vals]
        p99 = [_get_metric(v, "latency_p99_ms", "latency_mean_ms") for v in vals]
        err = [_get_metric(v, "error_rate", "failure_rate") for v in vals]

        std = stdev(lats) if len(lats) > 1 else 0.0
        summary.append(
            {
                "method": method,
                "scale": scale,
                "security": security,
                "latency_mean_ms": mean(lats),
                "latency_std_ms": std,
                "latency_median_ms": median(lats),
                "throughput_mean": mean(thr),
                "throughput_std": stdev(thr) if len(thr) > 1 else 0.0,
                "error_rate_mean": mean(err),
                "p50": mean(p50),
                "p95": mean(p95),
                "p99": mean(p99),
                "runs": len(vals),
            }
        )
        se = (std / math.sqrt(len(lats))) if lats else 0.0
        mu = mean(lats)
        ci_rows.append(
            {
                "method": method,
                "scale": scale,
                "security": security,
                "mean": mu,
                "std": std,
                "count": len(lats),
                "ci95_low": mu - 1.96 * se,
                "ci95_high": mu + 1.96 * se,
            }
        )

    _write_csv(out / "summary.csv", summary, list(summary[0].keys()))
    _write_csv(out / "confidence_intervals.csv", ci_rows, list(ci_rows[0].keys()))
    return rows, summary, ci_rows
