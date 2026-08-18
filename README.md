# IndustrialSemanticInterop

> **Adaptive benchmarking of industrial semantic interoperability strategies under scale, security, and fault constraints.**

[![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-reproducible-2496ED?logo=docker&logoColor=white)](Dockerfile)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![AI2M4RI @ MobiSPC 2026](https://img.shields.io/badge/AI2M4RI%20%40%20MobiSPC%202026-Accepted%20%26%20Presented-success)](#citation)

**IndustrialSemanticInterop** is a reproducible research benchmark for comparing semantic interoperability strategies in industrial software systems. It evaluates how different mediation approaches behave when interoperability is stressed by **scale**, **security overhead**, **semantic ambiguity**, and **fault conditions**, while recording latency, throughput, resource use, robustness, and recovery-oriented metrics.

The repository accompanies the 2026 AI2M4RI/MobiSPC paper listed in the [Citation](#citation) section.

## Why this repository exists

Industrial interoperability is rarely a single-objective problem. A strategy that is fastest in a clean environment may become fragile under missing metadata, authentication failures, semantic mismatches, endpoint outages, or high load. This benchmark provides a controlled way to compare those trade-offs and to study **adaptive strategy selection** rather than assuming one interoperability mechanism is optimal for every operating condition.

## Research highlights

- **Five interoperability strategies**: `adaptive_selection`, `direct_translation`, `ontology_based`, `opcua_mediated`, and `soa`.
- **Six selection policies**: balanced, latency-first, semantics-first, security-first, fault-resilient, and adaptive-auto.
- **Three scale levels**: small, medium, and large.
- **Four security modes**: none, authentication, encryption, and full security.
- **Ten fault / constraint scenarios**, including missing metadata, ambiguous mappings, unit mismatch, service/endpoint outages, authentication failure, high load, and mixed constraints.
- **Deterministic experimentation** with a fixed seed (`4242`) and 20 repetitions in the default configuration.
- **Automated analysis pipeline** for aggregation, descriptive statistics, effect-size analysis, visualization, and report generation.
- **Containerized reproduction** using Python 3.12 and Docker.

## Evaluated strategies

| Strategy | Benchmark role |
|---|---|
| `direct_translation` | Low-overhead point-to-point translation baseline. |
| `ontology_based` | Semantically richer mediation with higher processing cost. |
| `opcua_mediated` | OPC UA-style mediated interoperability path. |
| `soa` | Service-oriented interoperability baseline. |
| `adaptive_selection` | Runtime selection of an interoperability strategy according to operating conditions and policy objectives. |

## Benchmark dimensions

The default experiment configuration is defined in [`configs/default.yaml`](configs/default.yaml).

| Dimension | Default configuration |
|---|---|
| Strategies | 5 |
| Selection policies | 6 |
| Scale levels | 3 |
| Security modes | 4 |
| Fault / constraint conditions | 10 |
| Repetitions | 20 |
| Random seed | 4242 |

The framework is intentionally configuration-driven so that individual dimensions can be reduced for smoke tests or extended for new experiments.

## Architecture

```mermaid
flowchart LR
    A[Scenario / Workload] --> B[Source Adapter]
    B --> C[Canonical Model]
    C --> D[Mapping / Semantic Transform]
    D --> E[Strategy or Adaptive Selector]
    E --> F[Target Adapter]
    F --> G[Validation]
    G --> H[Metrics & Instrumentation]
    H --> I[Aggregation / Statistics]
    I --> J[Figures & Reports]
```

The implementation is separated into adapters, canonical models, mappings, benchmark orchestration, strategy selection, scenario definitions, metrics, analysis, and reporting. See [`docs/architecture.md`](docs/architecture.md) for the execution flow.

## Quick start

### Docker — recommended

```bash
docker compose up --build
```

The container runs the default benchmark and mounts `./results` so generated outputs remain available on the host.

### Native Python

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m scripts.run_all
```

On Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:PYTHONPATH = "."
python -m scripts.run_all
```

### Run the framework directly

```bash
python -m framework_benchmark run --config configs/default.yaml
```

For a lighter configuration, start from [`configs/minimal.yaml`](configs/minimal.yaml).

## Outputs

Generated experiment artifacts are written below `results/`:

- `results/raw_runs/` — raw experiment observations
- `results/ablations/` — ablation experiments
- `results/robustness/` — fault and robustness experiments
- `results/aggregated/` — aggregated statistics
- `results/figures/` — publication-oriented figures
- `results/final_report.html` — generated HTML report
- `results/final_report.md` — generated Markdown report when produced by the full pipeline

## What the benchmark measures

The analysis code covers the following evidence categories:

- end-to-end and percentile latency
- throughput and scale sensitivity
- CPU and memory consumption
- security overhead
- fault-induced degradation and recovery behavior
- ablation effects
- confidence intervals and effect sizes
- latency / throughput / memory Pareto trade-offs

The repository includes plotting and report-generation utilities under [`analysis/`](analysis/).

## Result interpretation

The existing benchmark implementation is designed to test the following trade-offs:

- `adaptive_selection` targets stronger robustness across changing and faulted conditions;
- `direct_translation` provides the latency-oriented baseline;
- `ontology_based` represents a semantically richer but more resource-intensive path;
- the benchmark makes latency, throughput, robustness, and resource trade-offs explicit instead of collapsing performance into a single score.

Generated results should be interpreted together with the exact configuration, seed, environment, and scenario definitions used for the run.

## Scientific scope and claim boundary

This is a **research benchmark and prototype framework**, not a standards certification product.

- Experiments are executed in a **virtualized testbed**.
- The current repository does **not** provide hardware-in-the-loop validation.
- IEEE 1451-, IEC 61499-, and OPC UA-related components are **representative / standards-informed adapters and bridges**; the repository does not claim complete conformance certification.
- The framework supports reproducible scenario-driven evaluation with deterministic seeds.
- Descriptive analysis and effect-size tooling are included; claims of formal inferential significance should only be made when supported by an explicitly defined statistical test and experimental protocol.

See [`docs/paper_claim_boundary.md`](docs/paper_claim_boundary.md) and [`docs/benchmark_protocol.md`](docs/benchmark_protocol.md) for details.

## Repository layout

```text
IndustrialSemanticInterop/
├── adapters/              # Pluggable protocol-style adapters
├── analysis/              # Aggregation, statistics, plots, reports
├── benchmark/             # Benchmark orchestration and instrumentation
├── benchmarks/            # Scenario, robustness, and ablation runners
├── canonical_model/       # Canonical data model and validators
├── configs/               # Reproducible experiment configurations
├── docs/                  # Architecture, scope, methods, reproducibility
├── framework_benchmark/   # Main benchmark framework and adaptive policies
├── mappings/              # Semantic mapping and transforms
├── metrics/               # Timing, payload, network, and resource metrics
├── paper/                 # Paper-facing analysis material
├── scenarios/             # Reproducible scenario definitions
├── scripts/               # End-to-end execution entry points
├── templates/             # Report templates
└── tests/                 # Unit, scenario, integration, and smoke tests
```

## Reproducibility

For publication-oriented runs, record the Git commit, configuration file, Python/container version, host information, seed, and generated raw outputs. A reproducibility checklist and platform-specific commands are provided in [`docs/reproducibility.md`](docs/reproducibility.md).

Run the test suite with:

```bash
pytest -q
```

## Citation

If you use this repository, benchmark design, experimental framework, or derived results in academic work, please cite:

> Tavakkoli, V., Mohsenzadegan, K., & Kyamakya, K. (2026). **Adaptive Benchmarking of Industrial Semantic Interoperability Strategies under Scale, Security, and Fault Constraints.** Accepted and Presented at the International Workshop on AI and Mathematical Methods for Real-world Impact (AI2M4RI), in conjunction with the 23rd International Conference on Mobile Systems and Pervasive Computing (MobiSPC), Athens, Greece, August 18–20, 2026.

```bibtex
@inproceedings{tavakkoli2026adaptivebenchmarking,
  author    = {Tavakkoli, Vahid and Mohsenzadegan, Kabeh and Kyamakya, Kyandoghere},
  title     = {Adaptive Benchmarking of Industrial Semantic Interoperability Strategies under Scale, Security, and Fault Constraints},
  booktitle = {International Workshop on AI and Mathematical Methods for Real-world Impact (AI2M4RI), in conjunction with the 23rd International Conference on Mobile Systems and Pervasive Computing (MobiSPC)},
  address   = {Athens, Greece},
  year      = {2026},
  month     = aug,
  note      = {Accepted and presented, August 18--20, 2026}
}
```

GitHub-compatible citation metadata is also available in [`CITATION.cff`](CITATION.cff).

## Contributing

Contributions that improve reproducibility, add clearly scoped strategy baselines, strengthen tests, or extend scenario coverage are welcome. Please read [`CONTRIBUTING.md`](CONTRIBUTING.md) before proposing changes.

## Security

This repository evaluates security-related benchmark modes, but it is **not** itself a security enforcement product. Please follow [`SECURITY.md`](SECURITY.md) for responsible vulnerability reporting.

## License

Released under the [MIT License](LICENSE).