from itertools import product

METHODS = ["baseline", "direct_translation", "semantic_enriched"]
SECURITY_MODES = ["none", "auth", "encryption", "full"]
SCALES = ["small", "medium", "large"]


def build_scenarios():
    scenarios = []
    for method, scale, security in product(METHODS, SCALES, SECURITY_MODES):
        scenario_id = f"{method}__{scale}__{security}"
        scenarios.append(
            {
                "scenario_id": scenario_id,
                "method": method,
                "workload": scale,
                "scale": scale,
                "security": security,
            }
        )
    return scenarios
