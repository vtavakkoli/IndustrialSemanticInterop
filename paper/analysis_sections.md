# Analysis Sections for Paper Submission

## Ablation Study
Compared `full_framework` against `no_adaptive`, `no_fault_handling`, and `no_security_awareness` using medium-scale adaptive-selection runs.

| Variant | Mean Latency (ms) | Throughput (msg/s) |
|---|---:|---:|
| full_framework | 0.0036 | 35639.05 |
| no_adaptive | 0.0037 | 35054.48 |
| no_fault_handling | 0.0037 | 35608.09 |
| no_security_awareness | 0.0036 | 35511.46 |

## Robustness Analysis
| Fault Scenario | Failure Rate | Recovery Success Rate |
|---|---:|---:|
| missing_metadata | 0.0139 | 0.5361 |
| schema_mismatch | 0.0181 | 0.6165 |
| high_load | 0.0000 | 1.0000 |
| ambiguous_mapping | 0.0167 | 0.5774 |

## Adaptive Strategy Explanation
Adaptive policy selection uses context-aware ranking with fallback.
```text
policy <- infer_policy(latency_target, semantic_complexity, security_mode, fault_state)
ranked <- rank_strategies(policy, constraints)
for strategy in ranked:
    result <- execute(strategy)
    if result.success: return result
return degraded_mode_result
```

Policies:
- latency_first
- semantics_first
- security_first
- fault_resilient
- balanced

## Statistical Rigor
Mean/median/std/p95 latency and 95% confidence intervals are computed per method × scale × security cell. Pairwise method comparisons include Welch-style tests and Cohen's d.

| Method | Mean Latency | Throughput | Robustness | CPU | Memory |
|---|---:|---:|---:|---:|---:|
| adaptive_selection | 0.0040 ms | 32579.41 | 0.9941 | 0.48 | 0.00 MB |
| direct_translation | 0.0033 ms | 34271.87 | 0.9868 | 0.46 | 0.00 MB |
| ontology_based | 0.0042 ms | 33254.51 | 0.9868 | 0.44 | 0.00 MB |
| opcua_mediated | 0.0036 ms | 34837.01 | 0.9858 | 0.41 | 0.00 MB |
| soa | 0.0037 ms | 34680.56 | 0.9858 | 0.40 | 0.00 MB |
