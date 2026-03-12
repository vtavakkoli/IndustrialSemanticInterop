from __future__ import annotations

import argparse
import json
from pathlib import Path

from analysis.generate_report import generate_report
from analysis.aggregate_results import aggregate

from .config import load_config
from .runner import run_campaign, summarize_records, write_records
from .scenarios.definitions import SCENARIO_FLAGS


def _log(msg: str) -> None:
    print(msg, flush=True)


def cmd_run(args) -> None:
    _log(f"[framework_benchmark] loading config: {args.config}")
    cfg = load_config(args.config)
    _log("[framework_benchmark] running campaign")
    records = run_campaign(cfg, progress=_log)
    write_records(records, cfg["results"]["raw_dir"], progress=_log)
    Path(cfg["results"]["aggregated_dir"]).mkdir(parents=True, exist_ok=True)
    summary_path = Path(cfg["results"]["aggregated_dir"]) / "adaptive_summary.json"
    summary_path.write_text(json.dumps(summarize_records(records), indent=2), encoding="utf-8")
    _log(f"[framework_benchmark] wrote adaptive summary: {summary_path}")

    _log("[framework_benchmark] aggregating raw runs")
    aggregate(cfg["results"]["raw_dir"], cfg["results"]["aggregated_dir"])

    _log("[framework_benchmark] generating report")
    generate_report("results")
    _log("[framework_benchmark] run command completed")


def cmd_report(args) -> None:
    _log(f"[framework_benchmark] report command start (input={args.input})")
    if args.input:
        aggregate(args.input, "results/aggregated")
    generate_report("results")
    if args.output and args.output != "results/final_report.html":
        Path(args.output).write_text(Path("results/final_report.html").read_text(encoding="utf-8"), encoding="utf-8")
        _log(f"[framework_benchmark] copied report to: {args.output}")
    _log("[framework_benchmark] report command completed")


def cmd_scenarios(args) -> None:
    print("Available scenario flags:")
    for item in SCENARIO_FLAGS:
        print(f" - {item}")


def cmd_validate(args) -> None:
    _log(f"[framework_benchmark] validating config: {args.config}")
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
