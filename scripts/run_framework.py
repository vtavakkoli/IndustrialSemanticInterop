"""Run the modular interoperability benchmark pipeline end-to-end."""

from __future__ import annotations

import argparse
from pathlib import Path

from analysis.aggregate import aggregate_results
from analysis.report import generate_report
from analysis.statistics import build_descriptive_stats
from benchmark.runner import run_benchmarks


def _progress(step: str) -> None:
    print(f"[framework] {step}", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repetitions", type=int, default=20)
    parser.add_argument("--seed", type=int, default=4242)
    parser.add_argument("--synthetic-mode", action="store_true")
    parser.add_argument("--skip-plots", action="store_true")
    parser.add_argument("--output-dir", default="results/raw_runs")
    args = parser.parse_args()

    Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    _progress(
        f"starting benchmark run: repetitions={args.repetitions}, seed={args.seed}, "
        f"synthetic_mode={args.synthetic_mode}, output_dir={args.output_dir}"
    )
    run_benchmarks(output_dir=args.output_dir, repetitions=args.repetitions, base_seed=args.seed, synthetic_mode=args.synthetic_mode)

    _progress("aggregating run artifacts")
    aggregate_results(raw_dir=args.output_dir, output_dir="results/aggregated")

    _progress("computing descriptive statistics")
    build_descriptive_stats("results/aggregated/summary.json")

    if args.skip_plots:
        _progress("skipping plot generation (--skip-plots)")
    else:
        _progress("generating figures")
        from analysis.plots import plot_latency

        plot_latency("results/aggregated/summary.json", "results/figures")

    _progress("generating markdown report")
    generate_report("results")
    _progress("pipeline completed successfully")


if __name__ == "__main__":
    main()
