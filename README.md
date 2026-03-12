# Modular Interoperability Benchmarking Framework (Prototype)

This repository provides a **reproducible interoperability benchmarking framework** for industrial data exchange pipelines.

## What is implemented
- Modular benchmark engine with reproducible seeds and scenario-driven execution.
- Pluggable protocol adapter interface (`ProtocolAdapter`) with representative adapters:
  - `ieee1451_style` (source/TEDS-like metadata path)
  - `iec61499_style` (function-block exchange payload path)
  - `opcua_bridge` (OPC UA node-write exchange payload path)
  - `hybrid_pipeline` (OPC UA + IEC 61499 representative chain)
- Canonical intermediate message model used by semantic and bridge paths.
- Explicit JSON scenarios with expected outputs and validation criteria.
- Structured metrics and descriptive-statistics analysis pipeline.
- Automatic full method×scale×security matrix expansion for every base scenario template.
- Comprehensive publication-style HTML report generation with full figure set (`figure_01`..`figure_18`).

## Scope honesty
This is a **prototype framework** with **representative adapters**. It does not claim full standard compliance with IEEE 1451, IEC 61499, or OPC UA stacks.

See:
- `docs/protocol_scope.md`
- `docs/limitations.md`
- `docs/paper_claim_boundary.md`

## Quickstart (local Python)
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m scripts.run_framework --repetitions 100 --seed 4242
```

## Quickstart (Docker)
```bash
docker compose up --build
```

The Docker run executes the full pipeline and streams progress lines to stdout such as:
- `[framework] starting benchmark run ...`
- `[benchmark] run 400/24000 (1.7%) complete ...`
- `[framework] generating comprehensive final_report.html`
- `[framework] pipeline completed successfully`

## Outputs
Generated under `results/`:
- `raw_runs/*.json`
- `aggregated/runs.csv`
- `aggregated/summary.json` and `aggregated/summary.csv`
- `aggregated/descriptive_stats.json`
- `figures/figure_01_*.png` ... `figures/figure_18_*.png`
- `final_report.md`
- `final_report.html` (comprehensive, with figures embedded)
- `figure_table_provenance.json`

## Minimal reproducible benchmark command
```bash
python -m benchmark.runner --repetitions 100 --base-seed 4242
```

## Optional modes
```bash
# Skip modular single-plot stage only
python -m scripts.run_framework --skip-plots

# Skip comprehensive HTML+18-figure stage
python -m scripts.run_framework --skip-comprehensive-report
```

## Deprecated legacy benchmark path
The older synthetic harness in `benchmarks/` remains for backward compatibility but is not the recommended evidence path for publication claims.
