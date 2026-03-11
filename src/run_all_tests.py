"""
Entry point to generate dynamic performance metrics and final results.

Unlike the original implementation, this script no longer uses
predefined values from the paper.  Instead, it invokes a test
harness that exercises the ontology mapping, semantic reasoner and
wrapper service components to derive empirical performance metrics.
Those metrics are written to ``performance_metrics.json`` and
``performance_summary.csv`` in the specified results directory, and
the figure generation logic from ``generate_final_results`` is then
invoked to produce a complete set of plots and tables.

Running this script will populate ``performance_metrics.json`` and
``performance_summary.csv`` under the output directory and create the
``figures`` and ``enhanced_figures`` subdirectories containing all
plots.  The default output directory is ``results``.

Usage::

    python run_all_tests.py --output_dir path/to/output
"""
from __future__ import annotations

import argparse
import json
import os
from typing import Dict, List

import pandas as pd

# Import modules relative to this package when available.  When the
# script is executed in a stand‑alone context (e.g. ``python code/run_all_tests.py``),
# fall back to absolute imports.  This dual import strategy ensures
# compatibility across different execution environments.
try:
    from .generate_final_results import generate_results  # type: ignore
    from .compute_metrics import compute_metrics  # type: ignore
except Exception:
    from generate_final_results import generate_results  # type: ignore
    from compute_metrics import compute_metrics  # type: ignore


def write_metrics(metrics: dict, summary: list[dict], output_dir: str) -> None:
    """Write computed metrics and summary to disk.

    Args:
        metrics: Dictionary of performance metrics.
        summary: List of summary rows.
        output_dir: Directory where results will be written.
    """
    os.makedirs(output_dir, exist_ok=True)
    metrics_path = os.path.join(output_dir, "performance_metrics.json")
    summary_path = os.path.join(output_dir, "performance_summary.csv")
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)
    df = pd.DataFrame(summary)
    df.to_csv(summary_path, index=False)


def run_all(output_dir: str = "results") -> None:
    """Execute tests, compute metrics and generate result figures.

    This function runs the empirical test harness to derive metrics,
    writes them to disk and then invokes the figure generation logic.

    Args:
        output_dir: Directory in which to place metrics and figures.
    """
    # Run tests to compute metrics and summary
    metrics, summary = compute_metrics()
    # Persist metrics and summary
    write_metrics(metrics, summary, output_dir)
    # Generate plots and tables based on these metrics
    generate_results(output_dir)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate performance metrics and final results.")
    parser.add_argument(
        "--output_dir",
        type=str,
        default="results",
        help="Directory to write metrics and results (default: results)",
    )
    args = parser.parse_args()
    run_all(args.output_dir)


if __name__ == "__main__":
    main()