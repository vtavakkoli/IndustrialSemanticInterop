"""Run the modular interoperability benchmark pipeline end-to-end."""

from __future__ import annotations

import argparse
import json
import platform
import subprocess
from pathlib import Path

from analysis.aggregate import aggregate_results
from analysis.aggregate_results import aggregate as aggregate_comprehensive
from analysis.effect_sizes import compute_effect_sizes
from analysis.generate_report import generate_report as generate_comprehensive_report
from analysis.plot_all import plot_all
from analysis.report import generate_report
from analysis.statistics import build_descriptive_stats
from analysis.stats_analysis import run_stats
from analysis.validate_figures import validate_readable_text
from benchmark.runner import run_benchmarks


def _progress(step: str) -> None:
    print(f"[framework] {step}", flush=True)


def _write_environment(results_root: str = "results") -> None:
    env = Path(results_root) / "environment"
    env.mkdir(parents=True, exist_ok=True)
    (env / "system_info.json").write_text(
        json.dumps({"platform": platform.platform(), "python": platform.python_version()}, indent=2),
        encoding="utf-8",
    )
    try:
        pkg = subprocess.check_output(["python", "-m", "pip", "freeze"], text=True)
    except Exception:
        pkg = "unavailable\n"
    (env / "package_versions.txt").write_text(pkg, encoding="utf-8")
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        commit = "unknown"
    (env / "git_commit.txt").write_text(commit + "\n", encoding="utf-8")


def _run_comprehensive_report_pipeline(results_root: str = "results") -> None:
    _progress("running comprehensive aggregation/statistics for HTML report")
    rows, _, _ = aggregate_comprehensive(f"{results_root}/raw_runs", f"{results_root}/aggregated")
    run_stats(rows, f"{results_root}/aggregated")
    compute_effect_sizes(rows, f"{results_root}/aggregated/effect_sizes.csv")

    _progress("rendering full figure set (figure_01..figure_18)")
    plot_all(rows)
    try:
        validate_readable_text()
    except Exception as exc:
        _progress(f"font validation warning: {exc}")

    _write_environment(results_root)
    _progress("generating comprehensive final_report.html")
    generate_comprehensive_report(results_root)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repetitions", type=int, default=100)
    parser.add_argument("--seed", type=int, default=4242)
    parser.add_argument("--synthetic-mode", action="store_true")
    parser.add_argument("--skip-plots", action="store_true")
    parser.add_argument("--output-dir", default="results/raw_runs")
    parser.add_argument("--skip-comprehensive-report", action="store_true")
    args = parser.parse_args()

    Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    _progress(
        f"starting benchmark run: repetitions={args.repetitions}, seed={args.seed}, "
        f"synthetic_mode={args.synthetic_mode}, output_dir={args.output_dir}"
    )
    run_benchmarks(output_dir=args.output_dir, repetitions=args.repetitions, base_seed=args.seed, synthetic_mode=args.synthetic_mode)

    _progress("aggregating run artifacts (modular summary)")
    aggregate_results(raw_dir=args.output_dir, output_dir="results/aggregated")

    _progress("computing descriptive statistics (modular summary)")
    build_descriptive_stats("results/aggregated/summary.json")

    if args.skip_plots:
        _progress("skipping modular plot generation (--skip-plots)")
    else:
        _progress("generating modular latency figure")
        from analysis.plots import plot_latency

        plot_latency("results/aggregated/summary.json", "results/figures")

    _progress("generating modular markdown report")
    generate_report("results")

    if args.skip_comprehensive_report:
        _progress("skipping comprehensive HTML report (--skip-comprehensive-report)")
    else:
        _run_comprehensive_report_pipeline("results")

    _progress("pipeline completed successfully")


if __name__ == "__main__":
    main()
