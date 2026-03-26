import argparse
from pathlib import Path

from .export_results import export_json
from .run_trial import run_trial
from .scenario_matrix import build_scenarios
from .validate_results import validate_result


def run_benchmarks(repetitions: int = 5, output: str = "results/raw_runs"):
    paths = []
    for scenario in build_scenarios():
        for run_index in range(repetitions):
            seed = 1000 + run_index
            result = run_trial(scenario, run_index, seed)
            validate_result(result)
            paths.append(export_json(result, output))
    return paths


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repetitions", type=int, default=5)
    parser.add_argument("--output", default="results/raw_runs")
    args = parser.parse_args()
    Path(args.output).mkdir(parents=True, exist_ok=True)
    run_benchmarks(repetitions=args.repetitions, output=args.output)


if __name__ == "__main__":
    main()
