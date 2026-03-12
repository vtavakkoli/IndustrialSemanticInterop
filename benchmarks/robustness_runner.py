from .export_results import export_json
from .run_trial import run_trial
from .scenario_matrix import build_scenarios
from .validate_results import validate_result

FAULTS = ["packet_drop", "malformed_payload", "delayed_downstream", "dependency_restart", "semantic_service_failure", "burst_overload"]


def run_robustness(repetitions: int = 3, output: str = "results/robustness"):
    paths = []
    scenarios = [s for s in build_scenarios() if s["scale"] == "medium"]
    for scenario in scenarios:
        for fault in FAULTS:
            for run_index in range(repetitions):
                result = run_trial(scenario, run_index, 3000 + run_index, fault=fault)
                validate_result(result)
                paths.append(export_json(result, output))
    return paths
