# Industrial Semantic Interoperability — Reproducible Benchmark Framework

This repository now produces a complete, publication-ready benchmark package under `results/` from a single command.

## Full end-to-end run (Docker)
```bash
docker compose up --build
```
The container runs `python -m scripts.run_all` and writes all outputs to `results/` on the host.

## Full end-to-end run (Python-native)
```bash
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m scripts.run_all
```

## Output package
```
results/
  raw_runs/
  aggregated/
  ablations/
  robustness/
  figures/
  environment/
  manifest.json
  figure_table_provenance.json
  final_report.html
  final_report.md
```

## What is generated automatically
- Full scenario matrix benchmark runs with repetitions.
- Ablation experiments.
- Robustness/fault-injection experiments.
- Aggregated tables (`summary`, `confidence_intervals`, `stat_tests`, `posthoc`, `effect_sizes`).
- 18 benchmark figures:
  - `figure_01_experiment_matrix.png`
  - `figure_02_latency_distribution.png`
  - `figure_03_latency_p95_comparison.png`
  - `figure_04_throughput_comparison.png`
  - `figure_05_throughput_vs_scale.png`
  - `figure_06_scalability_latency.png`
  - `figure_07_scalability_resources.png`
  - `figure_08_security_latency_overhead.png`
  - `figure_09_security_throughput_overhead.png`
  - `figure_10_cpu_usage.png`
  - `figure_11_memory_usage.png`
  - `figure_12_ablation_impact_latency.png`
  - `figure_13_ablation_impact_throughput.png`
  - `figure_14_robustness_degradation.png`
  - `figure_15_recovery_success.png`
  - `figure_16_confidence_intervals.png`
  - `figure_17_effect_sizes.png`
  - `figure_18_pareto_tradeoff.png`
- Structured HTML report with chart explanations and reproducibility metadata.

## Run only one stage
```bash
python -m benchmarks.benchmark_runner --repetitions 3 --output results/raw_runs
```

## Failed run handling
Malformed run artifacts cause aggregation failure (fail-loud), preventing silent bias.

## Known limitations
- Network counters are host-level approximations (`/proc/net/dev`) and can include unrelated traffic.
- Fault model is controlled synthetic injection and does not emulate all hardware faults.
- Statistical stage currently uses conservative proxy logic in dependency-minimal mode.

## Attribution
Writen by Dr. Vahid Tavakkoli 2026

## License
This project is licensed under the MIT License. See `LICENSE`.
