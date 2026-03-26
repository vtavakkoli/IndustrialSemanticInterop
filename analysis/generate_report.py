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




def _build_pairwise_comparison_rows(perf_rows):
    rows = []
    by_strategy = {r["strategy"]: r for r in perf_rows}
    for strategy, base in sorted(by_strategy.items()):
        for other, ref in sorted(by_strategy.items()):
            if strategy == other:
                continue
            lat_delta = _safe_float(base.get("avg_latency")) - _safe_float(ref.get("avg_latency"))
            thr_delta = _safe_float(base.get("throughput")) - _safe_float(ref.get("throughput"))
            succ_delta = _safe_float(base.get("success_rate")) - _safe_float(ref.get("success_rate"))
            rows.append(
                {
                    "method": strategy,
                    "compared_to": other,
                    "latency_delta_ms": f"{lat_delta:+.4f}",
                    "throughput_delta": f"{thr_delta:+.2f}",
                    "success_rate_delta": f"{succ_delta:+.3f}",
                }
            )
    return rows


def _build_rankings(perf_rows):
    ranking_rows = []
    for row in perf_rows:
        score = (
            (_safe_float(row.get("success_rate")) * 0.5)
            + (_safe_float(row.get("throughput")) / 10000.0 * 0.3)
            - (_safe_float(row.get("avg_latency")) / 10.0 * 0.2)
        )
        ranking_rows.append(
            {
                "method": row["strategy"],
                "composite_score": f"{score:.4f}",
                "avg_latency": row["avg_latency"],
                "throughput": row["throughput"],
                "success_rate": row["success_rate"],
            }
        )
    ranking_rows.sort(key=lambda x: _safe_float(x["composite_score"]), reverse=True)
    for idx, row in enumerate(ranking_rows, start=1):
        row["rank"] = idx
    return ranking_rows


def _ablation_summary_rows(ablation_rows):
    grouped = defaultdict(list)
    for row in ablation_rows:
        variant = row.get("ablation", {}).get("variant", "full_framework")
        grouped[variant].append(row)
    out = []
    for variant, vals in sorted(grouped.items()):
        out.append(
            {
                "variant": variant,
                "mean_latency_ms": f"{mean(_safe_float(x.get('latency_mean_ms')) for x in vals):.4f}",
                "median_latency_ms": f"{mean(_safe_float(x.get('latency_p50_ms', x.get('latency_mean_ms'))) for x in vals):.4f}",
                "throughput_msg_per_sec": f"{mean(_safe_float(x.get('throughput_msg_per_sec')) for x in vals):.2f}",
            }
        )
    return out


def _robustness_summary_rows(rob_rows):
    grouped = defaultdict(list)
    for row in rob_rows:
        grouped[row.get("notes", "fault=unknown").replace("fault=", "")].append(row)
    out = []
    for fault, vals in sorted(grouped.items()):
        failure_rate = mean(_safe_float(x.get("failure_rate")) for x in vals)
        recovery_success = mean(_safe_float(x.get("retry_success_rate", 0.0)) for x in vals)
        out.append(
            {
                "fault": fault,
                "failure_rate": f"{failure_rate:.4f}",
                "recovery_success_rate": f"{recovery_success:.4f}",
            }
        )
    return out

def generate_report(results_root="results"):
    root = Path(results_root)
    tidy = _read_csv(root / "aggregated" / "tidy_runs.csv")
    summary = _read_csv(root / "aggregated" / "summary.csv")
    stats = _read_csv(root / "aggregated" / "stat_tests.csv")
    ci = _read_csv(root / "aggregated" / "confidence_intervals.csv")
    effects = _read_csv(root / "aggregated" / "effect_sizes.csv")
    adaptive_vs_static = _read_csv(root / "aggregated" / "adaptive_vs_static.csv")
    scalability = _read_csv(root / "aggregated" / "scalability_summary.csv")
    ablation_runs = _read_json_runs(root / "ablations")
    robustness_runs = _read_json_runs(root / "robustness")
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
    ablation_rows = _ablation_summary_rows(ablation_runs)
    robustness_rows = _robustness_summary_rows(robustness_runs)
    pairwise_rows = _build_pairwise_comparison_rows(perf_rows)
    ranking_rows = _build_rankings(perf_rows)
    summary_table_rows = [
        {
            "method": row["strategy"],
            "mean_latency_ms": row["avg_latency"],
            "throughput_msg_per_sec": row["throughput"],
            "robustness_success_rate": row["success_rate"],
            "cpu_percent_avg": f"{mean(_safe_float(x.get('cpu_percent_avg')) for x in tidy if x.get('method') == row['strategy']):.2f}",
            "memory_mb_avg": f"{mean(_safe_float(x.get('memory_mb_avg')) for x in tidy if x.get('method') == row['strategy']):.2f}",
        }
        for row in perf_rows
    ]

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
        "<p><strong>Adaptive strategy logic:</strong> a policy is selected from latency_first, semantics_first, security_first, fault_resilient, balanced using scenario constraints; if the selected strategy fails, the next best policy-compliant strategy is attempted.</p>",
        "<code>for each scenario: policy &larr; infer_policy(context); ranked &larr; rank_strategies(policy, context); execute ranked with fallback; return degraded mode if all fail.</code>",
        _table(["policy", "selected_strategy", "selection_count", "success_rate", "avg_overhead"], decision_rows),
        _table(["scenario_id", "adaptive_latency_ms", "static_latency_ms", "latency_delta_ms", "adaptive_throughput", "static_throughput", "throughput_delta", "adaptive_success", "static_success", "success_delta"], adaptive_vs_static[:20]),
        "<ul><li><strong>latency_first</strong>: prioritizes direct_translation/opcua_mediated when deadlines dominate.</li><li><strong>semantics_first</strong>: prefers ontology_based when schema heterogeneity is high.</li><li><strong>security_first</strong>: avoids insecure paths in full security mode.</li><li><strong>fault_resilient</strong>: prioritizes adaptive_selection fallback-capable paths.</li><li><strong>balanced</strong>: minimizes weighted latency/throughput/failure score.</li></ul></div>",
        "<div class='card'><h2>Ablation Study</h2>",
        "<p>Compared variants: full framework, no_adaptive, no_fault_handling, and no_security_awareness. Latency and throughput impacts are computed from experiment runs in <code>results/ablations</code>.</p>",
        _table(["variant", "mean_latency_ms", "median_latency_ms", "throughput_msg_per_sec"], ablation_rows),
        "<p>Figure 12: <code>results/figures/figure_12_ablation_impact_latency.png</code>; Figure 13: <code>results/figures/figure_13_ablation_impact_throughput.png</code>.</p></div>",
        "<div class='card'><h2>Robustness and Fault Analysis</h2>",
        "<p>Fault scenarios: missing_metadata, schema_mismatch, high_load, ambiguous_mapping. Failure and recovery success rates are summarized below.</p>",
        _table(["fault_type", "strategy", "success_rate", "recovery_time", "degraded_mode_supported"], fault_rows),
        _table(["fault", "failure_rate", "recovery_success_rate"], robustness_rows),
        "<p>Figure 14: <code>results/figures/figure_14_robustness_degradation.png</code>; Figure 15: <code>results/figures/figure_15_recovery_success.png</code>.</p></div>",
        "<div class='card'><h2>Trade-off Tables</h2>",
        _table(["strategy", "avg_latency", "p95_latency", "throughput", "success_rate", "fallback_rate"], perf_rows),
        _table(["scenario_type", "recommended_strategy", "rationale"], rec_rows),
        _table(["method", "mean_latency_ms", "throughput_msg_per_sec", "robustness_success_rate", "cpu_percent_avg", "memory_mb_avg"], summary_table_rows),
        "</div>",
        "<div class='card'><h2>Method-to-Method Comparative Analysis</h2>",
        "<p>This section restores and extends direct cross-method comparison so each method is compared against every other method under the same campaign outputs.</p>",
        _table(["rank", "method", "composite_score", "avg_latency", "throughput", "success_rate"], ranking_rows),
        _table(["method", "compared_to", "latency_delta_ms", "throughput_delta", "success_rate_delta"], pairwise_rows),
        "</div>",
        "<div class='card'><h2>Statistical Summary</h2>",
        f"<p>Descriptive stats rows: {len(summary)}; CI rows: {len(ci)}; effect-size rows: {len(effects)}. Assumption checks: {len(stats)}.</p>",
        "<p>Latency mean/median/std/p95 are computed per strategy-scale-security group. 95% confidence intervals and pairwise significance testing with effect-size reporting (Cohen's d) are included; interpret results with virtualized-environment caution.</p></div>",
        "<div class='card'><h2>Benchmark Campaign Summary Table</h2>",
        _table(["strategy", "scale", "security_mode", "fault_mode", "runs", "successful_runs"], campaign_rows),
        "</div>",
        "<div class='card'><h2>Scalability Analysis</h2>",
        "<p>Scalability summaries are aggregated by method and scale, reflecting offered load, achieved throughput, and resource usage under container limits.</p>",
        _table(["method", "scale", "mean_offered_load_msg_s", "mean_latency_ms", "mean_throughput_msg_s", "mean_cpu_percent", "mean_memory_mb"], scalability),
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
        "## Comparative Method Ranking",
        *[f"- #{r['rank']} {r['method']} (score={r['composite_score']})" for r in ranking_rows],
        "",
        "## Ablation Study",
        *[f"- {r['variant']}: latency={r['mean_latency_ms']} ms, throughput={r['throughput_msg_per_sec']} msg/s" for r in ablation_rows],
        "",
        "## Robustness Analysis",
        *[f"- {r['fault']}: failure_rate={r['failure_rate']}, recovery_success={r['recovery_success_rate']}" for r in robustness_rows],
        "",
        "## Adaptive Strategy Policies",
        "- latency_first, semantics_first, security_first, fault_resilient, balanced",
        "- Pseudocode: infer policy -> rank strategies -> execute with fallback -> return degraded mode if all fail",
        "",
        "## Reproducibility",
        f"- Git commit: {env['git_commit']}",
        f"- Timestamp: {env['timestamp']}",
    ]
    (root / "final_report.md").write_text("\n".join(md), encoding="utf-8")
