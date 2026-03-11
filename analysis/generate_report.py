import csv
import json
from pathlib import Path


def _read_csv(path):
    with open(path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def generate_report(results_root="results"):
    root = Path(results_root)
    tidy = _read_csv(root / "aggregated" / "tidy_runs.csv")
    summary = _read_csv(root / "aggregated" / "summary.csv")
    stats = _read_csv(root / "aggregated" / "stat_tests.csv")

    best = min(summary, key=lambda r: float(r["latency_mean_ms"]))
    findings = f"Lowest average latency observed for: {best['method']} ({best['scale']}, {best['security']})."

    abl_files = list((root / "ablations").glob("*.json"))
    rob_files = list((root / "robustness").glob("*.json"))

    git_commit = (root / "environment" / "git_commit.txt").read_text().strip() if (root / "environment" / "git_commit.txt").exists() else "unknown"
    methods = sorted(set(r["method"] for r in tidy))

    text = f"""# Experimental Report

## Scope
Methods: {', '.join(methods)}
Scales: small, medium, large
Security modes: none, auth, encryption, full

## Key findings
{findings}

## Statistical significance
{stats}

## Ablation findings
Ablation runs: {len(abl_files)}

## Robustness findings
Robustness runs: {len(rob_files)}

## Limitations
Network counters are process-external and approximate for synthetic workload.

## Reproducibility metadata
Git commit: {git_commit}
Environment file: results/environment/system_info.json
"""
    (root / "final_report.md").write_text(text)
    (root / "final_report.html").write_text("<html><body><pre>" + text + "</pre></body></html>")

    provenance = {
        "figures": {
            "latency_distribution.svg": {"sources": ["results/aggregated/tidy_runs.csv"], "script": "analysis/plot_latency.py"},
            "throughput_vs_load.svg": {"sources": ["results/aggregated/tidy_runs.csv"], "script": "analysis/plot_throughput.py"},
        },
        "tables": {
            "summary.csv": {"sources": ["results/raw_runs/*.json"], "script": "analysis/aggregate_results.py"},
            "stat_tests.csv": {"sources": ["results/aggregated/tidy_runs.csv"], "script": "analysis/stats_analysis.py"},
        },
        "report_sections": {
            "key_findings": ["results/aggregated/summary.csv"],
            "statistical_significance": ["results/aggregated/stat_tests.csv"],
        },
    }
    (root / "figure_table_provenance.json").write_text(json.dumps(provenance, indent=2))
