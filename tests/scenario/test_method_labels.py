from benchmark.workloads import load_scenarios


IMPLEMENTED = {"direct_adapter", "semantic_mapping", "opcua_bridge", "hybrid_pipeline"}


def test_method_names_correspond_to_implemented_paths():
    for scenario in load_scenarios():
        assert scenario.method in IMPLEMENTED
