import platform
import random
import socket
import time
from datetime import datetime, timezone
from statistics import mean

from metrics.network_monitor import network_delta, read_network_counters
from metrics.payload_size import payload_size_bytes
from metrics.resource_monitor import ResourceMonitor
from metrics.startup_profiler import measure_startup

from .fault_injection import apply_fault
from .workload_profiles import WORKLOAD_PROFILES


def percentile(values, p):
    if not values:
        return 0.0
    values = sorted(values)
    k = (len(values) - 1) * (p / 100.0)
    f = int(k)
    c = min(f + 1, len(values) - 1)
    if f == c:
        return float(values[f])
    return float(values[f] + (values[c] - values[f]) * (k - f))


def _security_multiplier(mode: str) -> float:
    return {"none": 1.0, "auth": 1.05, "encryption": 1.12, "full": 1.18}[mode]


def _method_multiplier(method: str) -> float:
    return {"baseline": 1.0, "direct_translation": 1.06, "semantic_enriched": 1.14}[method]


def run_trial(scenario: dict, run_index: int, seed: int, fault: str | None = None, ablation: dict | None = None):
    rng = random.Random(seed)
    workload = WORKLOAD_PROFILES[scenario["workload"]]

    startup_ms = measure_startup(lambda: sum(i * i for i in range(7000)))
    monitor = ResourceMonitor()
    net_start = read_network_counters()
    monitor.start()

    latencies_ms = []
    sent = recv = 0
    dropped = errors = completed = retries = retry_success = 0

    started = datetime.now(timezone.utc)
    t0 = time.perf_counter()

    sec_mul = _security_multiplier(scenario["security"])
    meth_mul = _method_multiplier(scenario["method"])
    extra_mul = 1.0
    if ablation:
        extra_mul *= 0.94 if not ablation.get("cache", True) else 1.0
        extra_mul *= 0.92 if not ablation.get("reasoning", True) else 1.0
        extra_mul *= 1.03 if ablation.get("batching", False) else 1.0

    for _ in range(workload.message_count):
        payload = {
            "sensor_id": f"s-{rng.randint(1, 100000)}",
            "value": rng.uniform(35.0, 49.0),
            "ts": time.time(),
            "blob": "x" * max(1, workload.payload_size - 80),
        }
        psize = payload_size_bytes(payload)
        sent += psize
        t_msg = time.perf_counter()

        status = apply_fault(fault, rng) if fault else "ok"
        if status == "drop":
            dropped += 1
            continue
        if status in {"malformed", "semantic_failure"}:
            errors += 1
            retries += 1
            if rng.random() > 0.4:
                retry_success += 1
                completed += 1
            continue

        _ = payload["value"] * sec_mul * meth_mul * extra_mul
        for k in range(workload.concurrency * 10):
            _ = (k * 3) % 7
        latencies_ms.append((time.perf_counter() - t_msg) * 1000.0)
        recv += psize
        completed += 1

    duration = max(time.perf_counter() - t0, 1e-9)
    finished = datetime.now(timezone.utc)
    monitor.stop()
    net_end = read_network_counters()
    net = network_delta(net_start, net_end)

    latencies = latencies_ms or [0.0]
    result = {
        "scenario_id": scenario["scenario_id"] if not fault else f"{scenario['scenario_id']}__{fault}",
        "method": scenario["method"],
        "workload": scenario["workload"],
        "scale": scenario["scale"],
        "security": scenario["security"],
        "run_index": run_index,
        "seed": seed,
        "started_at": started.isoformat(),
        "finished_at": finished.isoformat(),
        "duration_sec": duration,
        "latency_mean_ms": float(mean(latencies)),
        "latency_p50_ms": percentile(latencies, 50),
        "latency_p95_ms": percentile(latencies, 95),
        "latency_p99_ms": percentile(latencies, 99),
        "throughput_msg_per_sec": float(completed / duration),
        "error_rate": float(errors / workload.message_count),
        "dropped_messages": dropped,
        "startup_time_ms": float(startup_ms),
        "cpu_percent_avg": monitor.cpu_avg,
        "memory_mb_avg": monitor.mem_avg,
        "network_bytes_sent": int(max(sent, net["bytes_sent"])),
        "network_bytes_recv": int(max(recv, net["bytes_recv"])),
        "payload_bytes_avg": float((sent / max(workload.message_count, 1))),
        "failure_rate": float((errors + dropped) / workload.message_count),
        "recovery_time_ms": float((retries - retry_success) * 1.0),
        "message_loss": int(dropped),
        "retry_success_rate": float((retry_success / retries) if retries else 1.0),
        "notes": "fault=" + (fault or "none"),
        "hostname": socket.gethostname(),
        "environment": {"platform": platform.platform(), "python": platform.python_version()},
        "ablation": ablation or {},
    }
    return result
