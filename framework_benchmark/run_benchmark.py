from __future__ import annotations

import argparse
import json
from pathlib import Path

from analysis.generate_report import generate_report
from analysis.aggregate_results import aggregate

from .config import load_config
from .runner import run_campaign, summarize_records, write_records
from .scenarios.definitions import SCENARIO_FLAGS


def cmd_run(args) -> None:
    cfg = load_config(args.config)
    records = run_campaign(cfg)
    write_records(records, cfg["results"]["raw_dir"])
    Path(cfg["results"]["aggregated_dir"]).mkdir(parents=True, exist_ok=True)
    (Path(cfg["results"]["aggregated_dir"]) / "adaptive_summary.json").write_text(
        json.dumps(summarize_records(records), indent=2), encoding="utf-8"
    )
    aggregate(cfg["results"]["raw_dir"], cfg["results"]["aggregated_dir"])
    generate_report("results")


def cmd_report(args) -> None:
    if args.input:
        aggregate(args.input, "results/aggregated")
    generate_report("results")
    if args.output and args.output != "results/final_report.html":
        Path(args.output).write_text(Path("results/final_report.html").read_text(encoding="utf-8"), encoding="utf-8")


def cmd_scenarios(args) -> None:
    print("Available scenario flags:")
    for item in SCENARIO_FLAGS:
        print(f" - {item}")


def cmd_validate(args) -> None:
    cfg = load_config(args.config)
    required = ["strategies", "scales", "security_modes", "repetitions", "seed"]
    for key in required:
        if key not in cfg:
            raise SystemExit(f"Missing required key: {key}")
    print("Configuration valid")


def main() -> None:
    parser = argparse.ArgumentParser(prog="framework_benchmark")
    sub = parser.add_subparsers(dest="command", required=True)

    run_parser = sub.add_parser("run", help="Run benchmark campaign")
    run_parser.add_argument("--config", default="configs/default.yaml")
    run_parser.set_defaults(func=cmd_run)

    report_parser = sub.add_parser("report", help="Generate report")
    report_parser.add_argument("--input", default="results/raw_runs")
    report_parser.add_argument("--output", default="results/final_report.html")
    report_parser.set_defaults(func=cmd_report)

    sc_parser = sub.add_parser("scenarios", help="List supported scenario flags")
    sc_parser.set_defaults(func=cmd_scenarios)

    val_parser = sub.add_parser("validate", help="Validate benchmark config")
    val_parser.add_argument("--config", default="configs/default.yaml")
    val_parser.set_defaults(func=cmd_validate)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
