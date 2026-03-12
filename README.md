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

## Scope honesty
This is a **prototype framework** with **representative adapters**. It does not claim full standard compliance with IEEE 1451, IEC 61499, or OPC UA stacks.

See:
- `docs/protocol_scope.md`
- `docs/limitations.md`
- `docs/paper_claim_boundary.md`

## Quickstart
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m scripts.run_framework --repetitions 20 --seed 4242
```

Outputs are written to `results/`:
- `raw_runs/*.json`
- `aggregated/summary.json`
- `aggregated/descriptive_stats.json`
- `figures/latency_summary.svg`
- `final_report.md`

## Minimal reproducible benchmark command
```bash
python -m benchmark.runner --repetitions 20 --base-seed 4242
```

## Generate paper-ready figures/tables
```bash
python -m analysis.aggregate
python -m analysis.statistics
python -m analysis.plots
python -m analysis.report
```

## Deprecated legacy benchmark path
The older synthetic harness in `benchmarks/` remains for backward compatibility but is not the recommended evidence path for publication claims.
