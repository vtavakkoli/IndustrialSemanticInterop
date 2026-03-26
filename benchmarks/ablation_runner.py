from .export_results import export_json
from .run_trial import run_trial
from .validate_results import validate_result


def run_ablations(repetitions: int = 3, output: str = "results/ablations"):
    variants = ["full_framework", "no_adaptive", "no_fault_handling", "no_security_awareness"]
    paths = []
    scenario = {"scenario_id": "ablation__adaptive_selection", "method": "adaptive_selection", "workload": "medium", "scale": "medium", "security": "full"}
    for variant in variants:
        abl = {"variant": variant}
        for run_index in range(repetitions):
            result = run_trial(scenario, run_index, 2000 + run_index, ablation=abl)
            result["scenario_id"] += f"__variant-{variant}"
            validate_result(result)
            paths.append(export_json(result, output))
    return paths
