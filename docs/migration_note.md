# Migration Note

The previous benchmark path relied on synthetic multipliers and generic method names (`baseline`, `direct_translation`, `semantic_enriched`).

This refactor introduces:
- method names tied to implemented paths (`direct_adapter`, `semantic_mapping`, `opcua_bridge`, `hybrid_pipeline`),
- explicit scenario JSON definitions,
- canonical-model-based translation path,
- stage-level measured metrics from actual adapter execution.

Legacy modules under `benchmarks/` are retained only for backward compatibility and are not the recommended publication evidence path.
