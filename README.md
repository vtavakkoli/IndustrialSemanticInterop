# Adaptive Interoperability Strategies Benchmark for Industrial Systems

This repository provides a reproducible benchmark for evaluating semantic interoperability strategies in industrial software stacks.

## Contribution

We benchmark adaptive strategy selection under realistic stressors:
- **Scale**: small, medium, and large workload profiles.
- **Security modes**: none, auth, encryption, full.
- **Fault conditions**: missing metadata, schema mismatch, high load, and ambiguous mappings.

Evaluated strategies:
- `adaptive_selection`
- `direct_translation`
- `ontology_based`
- `opcua_mediated`
- `soa`

## Key Results

- `adaptive_selection` delivers the best robustness profile under injected faults.
- `direct_translation` remains the lowest-latency path in latency-first scenarios.
- `ontology_based` incurs the highest compute and memory cost due to semantic processing overhead.
- The benchmark quantifies explicit latency/throughput/robustness trade-offs across methods.

## Reproducibility

### Full workflow (recommended)
```bash
docker-compose up --build
```

### Native workflow
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=. python scripts/run_all.py
```

### Running experiments only
```bash
python -m framework_benchmark run --config configs/default.yaml
```

### Output locations
- Raw experiment outputs: `results/raw_runs/`
- Ablation runs: `results/ablations/`
- Robustness runs: `results/robustness/`
- Aggregated statistics: `results/aggregated/`
- Figures: `results/figures/`
- Final report: `results/final_report.html`, `results/final_report.md`

## Repository Structure

- `/experiments` (benchmark execution entrypoints via `benchmarks/` and `scripts/`)
- `/results` (generated outputs)
- `/plots` (generated publication figures under `results/figures`)
- `/analysis` (aggregation, statistics, plotting, report generation)
- `/paper` (submission-facing narrative assets)

## Figures Overview (1–18)

1. Experiment matrix overview  
2. Latency distribution by method  
3. p95 latency comparison  
4. Throughput comparison  
5. Throughput vs scale  
6. Scalability impact on latency  
7. Scalability impact on resources  
8. Security overhead on latency  
9. Security overhead on throughput  
10. CPU usage by method  
11. Memory usage by method  
12. Ablation impact on latency  
13. Ablation impact on throughput  
14. Robustness degradation under faults  
15. Recovery success rate by fault  
16. Latency confidence intervals (95%)  
17. Pairwise effect sizes  
18. Pareto trade-off (latency/throughput/memory)

## Limitations

- Experiments are executed in a **virtualized testbed**.
- There is currently **no hardware-in-the-loop validation**.
- Implementations are standards-informed and do **not claim full standards compliance certification**.
