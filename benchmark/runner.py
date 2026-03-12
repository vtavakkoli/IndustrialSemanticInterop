"""Evidence-based benchmark runner for adapter pipelines."""

from __future__ import annotations

import argparse
import csv
import json
import logging
import random
import time
from pathlib import Path

from benchmark.instrumentation import read_resource_snapshot, stage_timer
from benchmark.metrics import BenchmarkResult
from benchmark.workloads import build_pipeline, load_scenarios

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
LOGGER = logging.getLogger("benchmark.runner")


def execute_once(scenario, run_index: int, seed: int, synthetic_mode: bool = False) -> BenchmarkResult:
    rng = random.Random(seed)
    stage_latency: dict[str, float] = {}

    startup_t0 = time.perf_counter()
    source, mapping_engine, target = build_pipeline(scenario.method)
    startup_overhead_ms = (time.perf_counter() - startup_t0) * 1000.0

    before = read_resource_snapshot()
    success = 0
    validations = 0
    expected = scenario.expected_output
    messages = scenario.benchmark_parameters["messages"]
    t0 = time.perf_counter()

    for _ in range(messages):
        source_payload = dict(scenario.payload)
        source_payload["measurement"] = scenario.payload["measurement"] + (rng.random() * 0.0001)

        with stage_timer("load_source", stage_latency):
            loaded = source.load_source(source_payload)
        with stage_timer("normalize_message", stage_latency):
            normalized = source.normalize_message(loaded)
        with stage_timer("map_to_canonical_model", stage_latency):
            canonical = source.map_to_canonical_model(normalized)
        with stage_timer("semantic_mapping", stage_latency):
            if scenario.method in {"semantic_mapping", "hybrid_pipeline"}:
                mapping_engine.rules = scenario.mapping_rules
                canonical = mapping_engine.apply(canonical)
        with stage_timer("translate_to_target", stage_latency):
            translated = target.translate_to_target(canonical)
        with stage_timer("send_to_target", stage_latency):
            sent = target.send_to_target(translated)

        if not synthetic_mode:
            success += 1
            if target.validate_roundtrip(sent, expected):
                validations += 1

    duration = max(time.perf_counter() - t0, 1e-9)
    after = read_resource_snapshot()

    return BenchmarkResult(
        scenario_id=scenario.scenario_id,
        method=scenario.method,
        run_index=run_index,
        seed=seed,
        repetitions=scenario.benchmark_parameters.get("repetitions", 1),
        measured=not synthetic_mode,
        synthetic_mode=synthetic_mode,
        success_rate=success / messages,
        validation_pass_rate=validations / messages,
        throughput_msg_per_sec=messages / duration,
        end_to_end_latency_ms=(duration / messages) * 1000.0,
        startup_overhead_ms=startup_overhead_ms,
        payload_bytes=float(len(json.dumps(scenario.payload))),
        cpu_time_sec=max(after.cpu_time_sec - before.cpu_time_sec, 0.0),
        memory_mb_max=max(after.max_rss_mb, before.max_rss_mb),
        stage_latency_ms=stage_latency,
        metadata={
            "source_protocol": scenario.source_protocol,
            "target_protocol": scenario.target_protocol,
            "description": scenario.description,
            "security": scenario.benchmark_parameters.get("security_mode", "none"),
            "estimated_metrics": {},
        },
    )


def run_benchmarks(output_dir: str = "results/raw_runs", repetitions: int = 20, base_seed: int = 4242, synthetic_mode: bool = False) -> list[Path]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    results: list[Path] = []
    scenarios = load_scenarios()

    total_runs = len(scenarios) * repetitions
    current_run = 0
    print(
        f"[benchmark] loaded {len(scenarios)} scenarios; repetitions={repetitions}; total_runs={total_runs}; synthetic_mode={synthetic_mode}",
        flush=True,
    )

    for scenario in scenarios:
        print(f"[benchmark] scenario start: {scenario.scenario_id} ({scenario.method})", flush=True)
        for run_index in range(repetitions):
            seed = base_seed + run_index
            result = execute_once(scenario, run_index=run_index, seed=seed, synthetic_mode=synthetic_mode)
            path = out / f"{scenario.scenario_id}__{scenario.method}__run{run_index:03d}.json"
            path.write_text(json.dumps(result.to_dict(), indent=2))
            results.append(path)
            current_run += 1
            progress = (current_run / total_runs) * 100.0 if total_runs else 100.0
            print(
                f"[benchmark] run {current_run}/{total_runs} ({progress:.1f}%) complete: "
                f"scenario={scenario.scenario_id} method={scenario.method} run={run_index} "
                f"latency_ms={result.end_to_end_latency_ms:.4f} throughput={result.throughput_msg_per_sec:.2f}",
                flush=True,
            )
            LOGGER.info("completed scenario=%s method=%s run=%d", scenario.scenario_id, scenario.method, run_index)
        print(f"[benchmark] scenario complete: {scenario.scenario_id}", flush=True)

    csv_path = out.parent / "aggregated" / "runs.csv"
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "scenario_id",
                "method",
                "run_index",
                "seed",
                "measured",
                "synthetic_mode",
                "success_rate",
                "validation_pass_rate",
                "throughput_msg_per_sec",
                "end_to_end_latency_ms",
                "startup_overhead_ms",
                "payload_bytes",
                "cpu_time_sec",
                "memory_mb_max",
            ],
        )
        writer.writeheader()
        for file in results:
            row = json.loads(file.read_text())
            writer.writerow({k: row[k] for k in writer.fieldnames})

    print(f"[benchmark] wrote {len(results)} run artifacts to {out}", flush=True)
    print(f"[benchmark] wrote aggregate CSV to {csv_path}", flush=True)
    return results


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="results/raw_runs")
    parser.add_argument("--repetitions", type=int, default=20)
    parser.add_argument("--base-seed", type=int, default=4242)
    parser.add_argument("--synthetic-mode", action="store_true")
    args = parser.parse_args()
    run_benchmarks(args.output_dir, args.repetitions, args.base_seed, args.synthetic_mode)


if __name__ == "__main__":
    main()
