from __future__ import annotations

from collections import defaultdict
from statistics import mean


def _avg(vals):
    return mean(vals) if vals else 0.0


def benchmark_campaign_summary(records: list[dict]) -> list[dict]:
    grp = defaultdict(list)
    for r in records:
        key = (r["strategy"], r["scale"], r["security_mode"], r["fault_mode"])
        grp[key].append(r)
    rows = []
    for (strategy, scale, sec, fault), vals in sorted(grp.items()):
        rows.append(
            {
                "strategy": strategy,
                "scale": scale,
                "security_mode": sec,
                "fault_mode": fault,
                "runs": len(vals),
                "successful_runs": sum(1 for v in vals if v["success"]),
            }
        )
    return rows


def headline_performance(records: list[dict]) -> list[dict]:
    grp = defaultdict(list)
    for r in records:
        grp[r["strategy"]].append(r)
    rows = []
    for strategy, vals in sorted(grp.items()):
        lats = sorted(v["latency"] for v in vals)
        p95 = lats[int((len(lats) - 1) * 0.95)] if lats else 0.0
        rows.append(
            {
                "strategy": strategy,
                "avg_latency": _avg([v["latency"] for v in vals]),
                "p95_latency": p95,
                "throughput": _avg([v["throughput"] for v in vals]),
                "success_rate": _avg([1.0 if v["success"] else 0.0 for v in vals]),
                "fallback_rate": _avg([1.0 if v["fallback_used"] else 0.0 for v in vals]),
            }
        )
    return rows


def adaptive_decisions(records: list[dict]) -> list[dict]:
    grp = defaultdict(list)
    for r in records:
        if r["strategy"] != "adaptive_selection":
            continue
        grp[(r["policy"], r["selected_strategy"])].append(r)
    rows = []
    for (policy, selected), vals in sorted(grp.items()):
        rows.append(
            {
                "policy": policy,
                "selected_strategy": selected,
                "selection_count": len(vals),
                "success_rate": _avg([1.0 if v["success"] else 0.0 for v in vals]),
                "avg_overhead": _avg([v["policy_overhead_ms"] for v in vals]),
            }
        )
    return rows


def fault_resilience(records: list[dict]) -> list[dict]:
    grp = defaultdict(list)
    for r in records:
        grp[(r["fault_mode"], r["strategy"])].append(r)
    rows = []
    for (fault, strategy), vals in sorted(grp.items()):
        rows.append(
            {
                "fault_type": fault,
                "strategy": strategy,
                "success_rate": _avg([1.0 if v["success"] else 0.0 for v in vals]),
                "recovery_time": _avg([v["recovery_time"] for v in vals]),
                "degraded_mode_supported": any(v["degraded_mode_supported"] for v in vals),
            }
        )
    return rows
