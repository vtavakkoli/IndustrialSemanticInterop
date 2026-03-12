"""Run the modular interoperability benchmark pipeline end-to-end."""

from __future__ import annotations

import argparse

from analysis.aggregate import aggregate_results
from analysis.plots import plot_latency
from analysis.report import generate_report
from analysis.statistics import build_descriptive_stats
from benchmark.runner import run_benchmarks


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repetitions", type=int, default=20)
    parser.add_argument("--seed", type=int, default=4242)
    parser.add_argument("--synthetic-mode", action="store_true")
    args = parser.parse_args()

    run_benchmarks(repetitions=args.repetitions, base_seed=args.seed, synthetic_mode=args.synthetic_mode)
    aggregate_results()
    build_descriptive_stats()
    plot_latency()
    generate_report()


if __name__ == "__main__":
    main()
