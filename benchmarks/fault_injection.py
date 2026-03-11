import random
import time


def apply_fault(fault: str, rng: random.Random):
    if fault == "packet_drop" and rng.random() < 0.05:
        return "drop"
    if fault == "malformed_payload" and rng.random() < 0.03:
        return "malformed"
    if fault == "delayed_downstream" and rng.random() < 0.08:
        time.sleep(0.002)
    if fault == "semantic_service_failure" and rng.random() < 0.02:
        return "semantic_failure"
    if fault == "burst_overload" and rng.random() < 0.07:
        time.sleep(0.001)
    if fault == "dependency_restart" and rng.random() < 0.01:
        time.sleep(0.004)
    return "ok"
