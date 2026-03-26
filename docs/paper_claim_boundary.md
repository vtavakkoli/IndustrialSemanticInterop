# Paper Claim Boundary

| Claim | Status | Evidence in repo | Recommended wording |
|---|---|---|---|
| Modular interoperability benchmark framework | supported | `adapters/`, `benchmark/`, `scenarios/` | "A modular prototype interoperability benchmarking framework." |
| Pluggable protocol adapters | supported | `adapters/base.py` + concrete adapters | "Pluggable representative protocol adapters." |
| IEEE 1451 / IEC 61499 / OPC UA support | partially supported | style/bridge adapters in `adapters/` | "Representative 1451-style, 61499-style, and OPC UA bridge adapters." |
| Full standards compliance | unsupported | N/A | "The current implementation is bounded and non-comprehensive." |
| Reproducible evaluation pipeline | supported | `benchmark/runner.py`, deterministic seeds, scenario JSON definitions | "Reproducible scenario-driven evaluation pipeline with deterministic seeds." |
| Inferential statistical significance | unsupported | `analysis/statistics.py` | "Descriptive results are reported; inferential analysis is future work." |
