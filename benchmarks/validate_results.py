REQUIRED_FIELDS = {
    "scenario_id", "method", "workload", "scale", "security", "run_index", "seed",
    "started_at", "finished_at", "duration_sec", "latency_mean_ms", "latency_p50_ms",
    "latency_p95_ms", "latency_p99_ms", "throughput_msg_per_sec", "error_rate",
    "dropped_messages", "startup_time_ms", "cpu_percent_avg", "memory_mb_avg",
    "network_bytes_sent", "network_bytes_recv", "payload_bytes_avg", "notes",
    "hostname", "environment",
}


def validate_result(result: dict):
    missing = REQUIRED_FIELDS - set(result)
    if missing:
        raise ValueError(f"Missing fields: {sorted(missing)}")
    if result["duration_sec"] <= 0:
        raise ValueError("duration_sec must be > 0")
    if result["throughput_msg_per_sec"] < 0:
        raise ValueError("throughput must be non-negative")
    return True
