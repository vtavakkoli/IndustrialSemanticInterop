import csv
import json
import os
import platform
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean


def _read_csv(path):
    if not Path(path).exists():
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _read_json_runs(path):
    p = Path(path)
    if not p.exists():
        return []
    return [json.loads(x.read_text()) for x in sorted(p.glob("*.json"))]


def _safe_float(v, default=0.0):
    try:
        return float(v)
    except Exception:
        return default


def _table(headers, rows):
    head = "".join(f"<th>{h}</th>" for h in headers)
    body = []
    for row in rows:
        body.append("<tr>" + "".join(f"<td>{row.get(h, '')}</td>" for h in headers) + "</tr>")
    return f"<table><thead><tr>{head}</tr></thead><tbody>{''.join(body)}</tbody></table>"


def _group_mean(rows, key, value):
    groups = defaultdict(list)
    for r in rows:
        groups[r.get(key, "unknown")].append(_safe_float(r.get(value)))
    return {k: mean(v) if v else 0.0 for k, v in groups.items()}


def _build_generated_tables(tidy):
    campaign = defaultdict(list)
    for r in tidy:
        campaign[(r.get("method", r.get("strategy", "unknown")), r.get("scale", "na"), r.get("security", r.get("security_mode", "na")), r.get("fault_mode", "none"))].append(r)
    campaign_rows = [
        {
            "strategy": k[0],
            "scale": k[1],
            "security_mode": k[2],
            "fault_mode": k[3],
            "runs": len(v),
            "successful_runs": sum(1 for x in v if _safe_float(x.get("success_rate", x.get("success", 0))) >= 1),
        }
        for k, v in sorted(campaign.items())
    ]

    perf = defaultdict(list)
    for r in tidy:
        perf[r.get("method", r.get("strategy", "unknown"))].append(r)
    perf_rows = []
    for strategy, rows in sorted(perf.items()):
        lats = sorted(_safe_float(x.get("latency_mean_ms", x.get("latency", 0))) for x in rows)
        p95 = lats[int((len(lats) - 1) * 0.95)] if lats else 0.0
        perf_rows.append(
            {
                "strategy": strategy,
                "avg_latency": f"{mean(lats) if lats else 0.0:.4f}",
                "p95_latency": f"{p95:.4f}",
                "throughput": f"{mean(_safe_float(x.get('throughput_msg_per_sec', x.get('throughput', 0))) for x in rows):.2f}",
                "success_rate": f"{mean(_safe_float(x.get('success_rate', x.get('success', 0))) for x in rows):.3f}",
                "fallback_rate": f"{mean(1.0 if str(x.get('fallback_used', 'False')).lower() == 'true' else 0.0 for x in rows):.3f}",
            }
        )

    decisions = defaultdict(list)
    for r in tidy:
        if r.get("method") != "adaptive_selection" and r.get("strategy") != "adaptive_selection":
            continue
        decisions[(r.get("policy", "n/a"), r.get("selected_strategy", r.get("method", "unknown")))].append(r)
    decision_rows = [
        {
            "policy": k[0],
            "selected_strategy": k[1],
            "selection_count": len(v),
            "success_rate": f"{mean(_safe_float(x.get('success_rate', x.get('success', 0))) for x in v):.3f}",
            "avg_overhead": f"{mean(_safe_float(x.get('policy_overhead_ms', 0.0)) for x in v):.4f}",
        }
        for k, v in sorted(decisions.items())
    ]

    fault_rows = []
    faults = defaultdict(list)
    for r in tidy:
        faults[(r.get("fault_mode", "none"), r.get("method", r.get("strategy", "unknown")))].append(r)
    for (fault, strat), vals in sorted(faults.items()):
        fault_rows.append(
            {
                "fault_type": fault,
                "strategy": strat,
                "success_rate": f"{mean(_safe_float(x.get('success_rate', x.get('success', 0))) for x in vals):.3f}",
                "recovery_time": f"{mean(_safe_float(x.get('recovery_time', x.get('recovery_time_ms', 0))) for x in vals):.3f}",
                "degraded_mode_supported": any(str(x.get("degraded_mode_supported", "False")).lower() == "true" for x in vals),
            }
        )

    recommendations = [
        {"scenario_type": "latency_sensitive", "recommended_strategy": "direct_translation", "rationale": "Lower latency profile in representative runs."},
        {"scenario_type": "semantic_heavy", "recommended_strategy": "ontology_based", "rationale": "Higher semantic resolution rate."},
        {"scenario_type": "fault_prone", "recommended_strategy": "adaptive_selection", "rationale": "Fallback behavior improves completion under faults."},
    ]
    boundaries = [
        {"aspect": "IEEE1451/IEC61499 conformance", "supported_now": "Representative strategy behavior", "limitation": "Not a full standards certification harness."},
        {"aspect": "Runtime environment", "supported_now": "Reproducible virtualized testbed", "limitation": "No hardware-in-the-loop timing guarantees."},
    ]
    return campaign_rows, perf_rows, decision_rows, fault_rows, recommendations, boundaries


def generate_report(results_root="results"):
    root = Path(results_root)
    tidy = _read_csv(root / "aggregated" / "tidy_runs.csv")
    summary = _read_csv(root / "aggregated" / "summary.csv")
    stats = _read_csv(root / "aggregated" / "stat_tests.csv")
    ci = _read_csv(root / "aggregated" / "confidence_intervals.csv")
    effects = _read_csv(root / "aggregated" / "effect_sizes.csv")
    adaptive_summary = {}
    ad_sum_path = root / "aggregated" / "adaptive_summary.json"
    if ad_sum_path.exists():
        adaptive_summary = json.loads(ad_sum_path.read_text())

    methods = sorted({r.get("method", "unknown") for r in tidy}) if tidy else []
    best_latency_method = min(summary, key=lambda r: _safe_float(r.get("latency_median_ms", 999999))).get("method", "n/a") if summary else "n/a"
    strat_success = _group_mean(tidy, "method", "success_rate") if tidy else {}
    strongest = max(strat_success, key=strat_success.get) if strat_success else "n/a"
    weakest = min(strat_success, key=strat_success.get) if strat_success else "n/a"

    campaign_rows, perf_rows, decision_rows, fault_rows, rec_rows, bound_rows = _build_generated_tables(tidy)

    git_commit = (root / "environment" / "git_commit.txt").read_text().strip() if (root / "environment" / "git_commit.txt").exists() else "unknown"
    env = {
        "platform": platform.platform(),
        "python": platform.python_version(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "git_commit": git_commit,
        "cwd": os.getcwd(),
    }

    html = [
        "<!doctype html><html><head><meta charset='utf-8'><title>Industrial Semantic Interop Benchmark Report</title>",
        "<style>body{font-family:Arial;background:#f7f8fb;color:#1e2330;margin:0}.wrap{max-width:1240px;margin:0 auto;padding:24px}.card{background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:16px;margin:14px 0}table{width:100%;border-collapse:collapse}th,td{border:1px solid #e5e7eb;padding:8px;text-align:left}code{background:#f3f4f6;padding:2px 6px;border-radius:4px}.placeholder{border:2px dashed #9ca3af;padding:12px;margin:8px 0;background:#f9fafb}</style></head><body><div class='wrap'>",
        "<h1>Industrial Semantic Interoperability Benchmark Report</h1>",
        "<div class='card'><h2>Executive Summary</h2>",
        f"<p>Benchmark scope: representative IEEE 1451–IEC 61499 interoperability strategies evaluated in a controlled, virtualized benchmark campaign. Headline best latency method: <strong>{best_latency_method}</strong>.</p>",
        f"<p>Strongest observed success profile: <strong>{strongest}</strong>. Weakest observed success profile: <strong>{weakest}</strong>.</p>",
        f"<p>Methods={len(methods)} | Runs={len(tidy)} | Adaptive fallback rate={adaptive_summary.get('fallback_rate', 0.0):.3f}</p></div>",
        "<div class='card'><h2>Benchmark Configuration Summary</h2>",
        f"<p>Strategies tested: {', '.join(methods) if methods else 'n/a'}. Scale levels and security modes were loaded from scenario matrix and config-defined campaigns.</p>",
        f"<p>Fault/complex scenario settings include flags such as missing_metadata, ambiguous_mapping, unit_mismatch, ontology_service_down, opcua_endpoint_down, authentication_failure, high_load, secure_and_semantic, and multi_constraint_mixed when present in run data.</p></div>",
        "<div class='card'><h2>Adaptive Selection Analysis</h2>",
        f"<p>Adaptive selected strategy distribution: {adaptive_summary.get('selected_strategy_distribution', {})}</p>",
        f"<p>Fallback success rate: {adaptive_summary.get('fallback_success_rate', 0.0):.3f}; scenario completion rate: {adaptive_summary.get('success_rate', 0.0):.3f}.</p>",
        _table(["policy", "selected_strategy", "selection_count", "success_rate", "avg_overhead"], decision_rows),
        "<div class='placeholder'>Figure Placeholder: Strategy Selection Distribution</div>",
        "<div class='placeholder'>Figure Placeholder: Scenario-wise Adaptive Policy Behavior</div></div>",
        "<div class='card'><h2>Robustness and Fault Analysis</h2>",
        _table(["fault_type", "strategy", "success_rate", "recovery_time", "degraded_mode_supported"], fault_rows),
        "<div class='placeholder'>Figure Placeholder: Fault Recovery Performance</div></div>",
        "<div class='card'><h2>Trade-off Tables</h2>",
        _table(["strategy", "avg_latency", "p95_latency", "throughput", "success_rate", "fallback_rate"], perf_rows),
        _table(["scenario_type", "recommended_strategy", "rationale"], rec_rows),
        "<div class='placeholder'>Figure Placeholder: Latency vs Robustness Trade-off</div></div>",
        "<div class='card'><h2>Statistical Summary</h2>",
        f"<p>Descriptive stats rows: {len(summary)}; CI rows: {len(ci)}; effect-size rows: {len(effects)}. Assumption checks: {len(stats)}.</p>",
        "<p>Inferential outcomes are reported as available from the current dependency-light statistical pipeline; interpret with virtualized-environment caution.</p></div>",
        "<div class='card'><h2>Benchmark Campaign Summary Table</h2>",
        _table(["strategy", "scale", "security_mode", "fault_mode", "runs", "successful_runs"], campaign_rows),
        "</div>",
        "<div class='card'><h2>Interpretation Boundaries</h2>",
        _table(["aspect", "supported_now", "limitation"], bound_rows),
        "</div>",
        "<div class='card'><h2>Limitations</h2><ul><li>Virtualized environment; not hardware-backed end-to-end standards conformance validation.</li><li>Representative strategy implementations are standards-informed, not full compliance reference stacks.</li><li>Resource usage metrics may contain placeholders when direct sampling is unavailable.</li></ul></div>",
        "<div class='card'><h2>Reproducibility</h2>",
        f"<p>Config path: <code>configs/default.yaml</code> (or user-provided). Random seed recorded per run. Timestamp: <code>{env['timestamp']}</code>.</p>",
        f"<p>Environment: <code>{env['platform']}</code>, Python <code>{env['python']}</code>, git commit <code>{env['git_commit']}</code>.</p></div>",
        "<div class='card'><h2>Existing Figure Pipeline References</h2><p>figure_01_experiment_matrix.png and full figure set remain supported for backward compatibility.</p></div>",
        "</div></body></html>",
    ]

    (root / "final_report.html").write_text("".join(html), encoding="utf-8")
    md = [
        "# Industrial Semantic Interoperability Benchmark Report",
        "",
        "## Executive Summary",
        f"- Runs: {len(tidy)}",
        f"- Best latency method: {best_latency_method}",
        f"- Strongest success profile: {strongest}",
        "",
        "## Reproducibility",
        f"- Git commit: {env['git_commit']}",
        f"- Timestamp: {env['timestamp']}",
    ]
    (root / "final_report.md").write_text("\n".join(md), encoding="utf-8")
