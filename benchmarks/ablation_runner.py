from itertools import product

from .export_results import export_json
from .run_trial import run_trial
from .scenario_matrix import METHODS
from .validate_results import validate_result


def run_ablations(repetitions: int = 3, output: str = "results/ablations"):
    toggles = {
        "reasoning": [True, False],
        "cache": [True, False],
        "translation": ["direct", "enriched"],
        "sync": [True, False],
        "batching": [True, False],
    }
    paths = []
    for method in METHODS:
        scenario = {"scenario_id": f"ablation__{method}", "method": method, "workload": "medium", "scale": "medium", "security": "full"}
        for vals in product(*toggles.values()):
            abl = dict(zip(toggles.keys(), vals))
            for run_index in range(repetitions):
                result = run_trial(scenario, run_index, 2000 + run_index, ablation=abl)
                result["scenario_id"] += "__" + "__".join(f"{k}-{v}" for k, v in abl.items())
                validate_result(result)
                paths.append(export_json(result, output))
    return paths
