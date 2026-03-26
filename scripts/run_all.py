import json
import platform
import subprocess
from pathlib import Path

from benchmarks.benchmark_runner import run_benchmarks
from benchmarks.ablation_runner import run_ablations
from benchmarks.robustness_runner import run_robustness
from analysis.aggregate_results import aggregate
from analysis.stats_analysis import run_stats
from analysis.effect_sizes import compute_effect_sizes
from analysis.plot_all import plot_all
from analysis.generate_report import generate_report
from analysis.validate_figures import validate_readable_text


def write_environment(results_root="results"):
    env = Path(results_root) / "environment"
    env.mkdir(parents=True, exist_ok=True)
    (env / "system_info.json").write_text(json.dumps({"platform": platform.platform(), "python": platform.python_version()}, indent=2))
    pkg = subprocess.check_output(["python", "-m", "pip", "freeze"], text=True)
    (env / "package_versions.txt").write_text(pkg)
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        commit = "unknown"
    (env / "git_commit.txt").write_text(commit + "\n")


def run_all(repetitions=5):
    root = Path("results")
    for sub in ["raw_runs", "aggregated", "ablations", "robustness", "figures", "environment"]:
        (root / sub).mkdir(parents=True, exist_ok=True)

    raw = run_benchmarks(repetitions=repetitions, output="results/raw_runs")
    abl = run_ablations(repetitions=max(2, repetitions // 2), output="results/ablations")
    rob = run_robustness(repetitions=max(2, repetitions // 2), output="results/robustness")

    df, _, _ = aggregate("results/raw_runs", "results/aggregated")
    run_stats(df, "results/aggregated")
    compute_effect_sizes(df, "results/aggregated/effect_sizes.csv")
    plot_all(df)
    validate_readable_text()
    write_environment("results")
    generate_report("results")

    manifest = {
        "raw_runs": len(raw),
        "ablations": len(abl),
        "robustness": len(rob),
        "outputs": [
            "results/aggregated/summary.csv",
            "results/aggregated/confidence_intervals.csv",
            "results/aggregated/stat_tests.csv",
            "results/aggregated/posthoc.csv",
            "results/aggregated/effect_sizes.csv",
            "results/final_report.md",
            "results/final_report.html",
        ],
        "figures": sorted([str(x) for x in (root / "figures").glob("figure_*.png")]),
        "font_validation": "results/figures/font_validation.json",
    }
    (root / "manifest.json").write_text(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    run_all()
