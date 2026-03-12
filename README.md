# Comparative Benchmarking Framework for Representative IEEE 1451–IEC 61499 Interoperability Strategies

This repository provides a **reproducible virtualized benchmark** for standards-informed, representative interoperability strategies between IEEE 1451-style and IEC 61499-style data flows.

## Project Purpose

This artifact supports comparative benchmarking under controlled scenario-based evaluation, including:
- baseline performance,
- robustness and fault tolerance,
- mixed requirement suitability,
- adaptive strategy selection behavior.

## Supported Strategies

- `ontology_based`
- `direct_translation`
- `soa`
- `opcua_mediated`
- `adaptive_selection`

Legacy method labels and benchmark scripts remain available for backward compatibility.

## Adaptive Selection Concept

`adaptive_selection` is a rule-based policy layer that selects a base strategy according to scenario features (latency sensitivity, semantic complexity, security level, interoperability breadth, fault mode, resource constraints) and supports fallback when an initial choice fails.

See `docs/adaptive_selection.md`.

## Execution Modes

### Docker mode
```bash
docker compose up --build
```

### Native Python mode
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m framework_benchmark run --config configs/default.yaml
python -m framework_benchmark report --input results/raw_runs --output results/final_report.html
```

## Unified CLI

- Run benchmark: `python -m framework_benchmark run --config configs/default.yaml`
- Generate report: `python -m framework_benchmark report --input results/raw_runs`
- List scenario flags: `python -m framework_benchmark scenarios`
- Validate config: `python -m framework_benchmark validate --config configs/default.yaml`

## Config Files

- `configs/default.yaml`
- `configs/adaptive_faults.yaml`
- `configs/minimal.yaml`

Configurable settings include strategies, policies, scales, security modes, scenario flags, repetitions, seeds, and output paths.

## Report Generation

The report pipeline extends `results/final_report.html` with publication-oriented sections:
- Executive summary,
- benchmark configuration summary,
- adaptive selection analysis,
- robustness/fault analysis,
- trade-off tables,
- statistical summary,
- limitations,
- reproducibility metadata,
- figure placeholders.

## Limitations

This repository does **not** claim full IEEE 1451 or IEC 61499 conformance testing. It implements representative strategy behavior in a virtualized environment.

## Reproducibility Guidance

- Use fixed seed configs (`configs/*.yaml`).
- Keep raw JSON outputs under `results/raw_runs`.
- Track environment metadata (`results/environment/*`).
- Capture git commit hash in generated artifacts.

More details in:
- `docs/scenarios.md`
- `docs/reporting.md`
- `docs/reproducibility.md`
- `docs/limitations.md`
