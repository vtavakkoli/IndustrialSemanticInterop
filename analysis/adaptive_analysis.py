import csv
from collections import defaultdict
from pathlib import Path
from statistics import mean


def _as_float(value, default=0.0):
    try:
        return float(value)
    except Exception:
        return default


def summarize_adaptive_vs_static(rows, out_dir: str = "results/aggregated"):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    by_scenario = defaultdict(lambda: {"adaptive": [], "static": []})
    for row in rows:
        bucket = "adaptive" if row.get("method", row.get("strategy")) == "adaptive_selection" else "static"
        by_scenario[row.get("scenario_id", "unknown")][bucket].append(row)

    records = []
    for scenario_id, groups in sorted(by_scenario.items()):
        if not groups["adaptive"] or not groups["static"]:
            continue
        adap = groups["adaptive"]
        stat = groups["static"]
        adap_latency = mean(_as_float(r.get("latency_mean_ms", r.get("latency"))) for r in adap)
        stat_latency = mean(_as_float(r.get("latency_mean_ms", r.get("latency"))) for r in stat)
        adap_thr = mean(_as_float(r.get("throughput_msg_per_sec", r.get("throughput"))) for r in adap)
        stat_thr = mean(_as_float(r.get("throughput_msg_per_sec", r.get("throughput"))) for r in stat)
        adap_success = mean(_as_float(r.get("success_rate", r.get("success"))) for r in adap)
        stat_success = mean(_as_float(r.get("success_rate", r.get("success"))) for r in stat)
        records.append(
            {
                "scenario_id": scenario_id,
                "adaptive_latency_ms": f"{adap_latency:.4f}",
                "static_latency_ms": f"{stat_latency:.4f}",
                "latency_delta_ms": f"{(adap_latency - stat_latency):+.4f}",
                "adaptive_throughput": f"{adap_thr:.2f}",
                "static_throughput": f"{stat_thr:.2f}",
                "throughput_delta": f"{(adap_thr - stat_thr):+.2f}",
                "adaptive_success": f"{adap_success:.4f}",
                "static_success": f"{stat_success:.4f}",
                "success_delta": f"{(adap_success - stat_success):+.4f}",
            }
        )

    with open(out / "adaptive_vs_static.csv", "w", newline="", encoding="utf-8") as f:
        fieldnames = list(records[0].keys()) if records else [
            "scenario_id", "adaptive_latency_ms", "static_latency_ms", "latency_delta_ms",
            "adaptive_throughput", "static_throughput", "throughput_delta",
            "adaptive_success", "static_success", "success_delta",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
    return records


def summarize_scalability(rows, out_dir: str = "results/aggregated"):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    groups = defaultdict(list)
    for row in rows:
        key = (
            row.get("method", row.get("strategy", "unknown")),
            row.get("scale", "unknown"),
        )
        groups[key].append(row)

    scale_order = {"small": 1, "medium": 2, "large": 3}
    records = []
    for (method, scale), vals in sorted(groups.items(), key=lambda x: (x[0][0], scale_order.get(x[0][1], 99))):
        records.append(
            {
                "method": method,
                "scale": scale,
                "mean_offered_load_msg_s": f"{mean(_as_float(v.get('offered_load_msg_per_sec', 0.0)) for v in vals):.2f}",
                "mean_latency_ms": f"{mean(_as_float(v.get('latency_mean_ms', v.get('latency', 0.0))) for v in vals):.4f}",
                "mean_throughput_msg_s": f"{mean(_as_float(v.get('throughput_msg_per_sec', v.get('throughput', 0.0))) for v in vals):.2f}",
                "mean_cpu_percent": f"{mean(_as_float(v.get('cpu_percent_avg', 0.0)) for v in vals):.2f}",
                "mean_memory_mb": f"{mean(_as_float(v.get('memory_mb_avg', 0.0)) for v in vals):.2f}",
            }
        )

    with open(out / "scalability_summary.csv", "w", newline="", encoding="utf-8") as f:
        fieldnames = list(records[0].keys()) if records else [
            "method", "scale", "mean_offered_load_msg_s", "mean_latency_ms", "mean_throughput_msg_s", "mean_cpu_percent", "mean_memory_mb",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
    return records
