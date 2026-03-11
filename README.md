# Industrial Semantic Interoperability — Reproducible Benchmark Pipeline

## Run full pipeline (Docker)
```bash
docker compose up --build
```
This automatically runs benchmark scenarios, repetitions, ablations, robustness runs, aggregation, statistics, figure generation, and report generation into `results/`.

## Run full pipeline (Python-native)
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m scripts.run_all
```

## Run a subset
```bash
python -m benchmarks.benchmark_runner --repetitions 3 --output results/raw_runs
```

## Regenerate analysis/figures/report from raw runs
```bash
python -m scripts.run_all
```

## Output structure
- `results/raw_runs/`
- `results/aggregated/`
- `results/ablations/`
- `results/robustness/`
- `results/figures/`
- `results/environment/`
- `results/manifest.json`
- `results/figure_table_provenance.json`
- `results/final_report.md`
- `results/final_report.html`

## Failed runs
Malformed run files raise errors in aggregation/stats stages (fail-loud behavior) to avoid silent bias.

## Known limitations
- Network byte counters include host process/network effects and are approximate for synthetic load.
- Fault injection currently targets controlled synthetic behaviors rather than external hardware faults.

## Reproducibility confirmations
- `docker compose up --build` produces the complete `results/` folder.
- `python -m scripts.run_all` uses the same core pipeline and produces the same structure.
