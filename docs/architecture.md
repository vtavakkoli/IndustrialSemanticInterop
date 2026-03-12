# Architecture

The framework is organized into separable layers:

- `benchmark/`: experiment orchestration, instrumentation, workload execution.
- `adapters/`: pluggable protocol adapters implementing a shared `ProtocolAdapter` interface.
- `canonical_model/`: canonical data model and validators.
- `mappings/`: semantic mapping rules and deterministic transforms.
- `scenarios/`: reproducible scenario definitions (YAML).
- `analysis/`: aggregation, descriptive statistics, plotting, and report generation.

Execution flow:
1. Source adapter loads + normalizes source payload.
2. Message maps to canonical model.
3. Optional semantic mapping rules apply.
4. Target adapter translates and sends payload.
5. Round-trip validation and stage-level metrics are recorded.
