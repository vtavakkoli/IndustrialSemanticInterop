# Benchmark Protocol

This document summarizes the default experimental protocol for **IndustrialSemanticInterop** and defines how benchmark results should be interpreted and reported.

## Research question

The benchmark studies how alternative industrial semantic interoperability strategies trade off latency, throughput, semantic mediation cost, resource use, and robustness when operating conditions vary across scale, security, and fault constraints.

A central research objective is to evaluate whether **adaptive strategy selection** can provide a stronger operating-point trade-off than selecting one fixed interoperability strategy for all conditions.

## Default experimental factors

The canonical configuration is [`configs/default.yaml`](../configs/default.yaml).

| Factor | Default values |
|---|---|
| Strategies | `ontology_based`, `direct_translation`, `soa`, `opcua_mediated`, `adaptive_selection` |
| Policies | `balanced`, `latency_first`, `semantics_first`, `security_first`, `fault_resilient`, `adaptive_auto` |
| Scale | `small`, `medium`, `large` |
| Security | `none`, `auth`, `encryption`, `full` |
| Repetitions | 20 |
| Seed | 4242 |

### Fault and constraint conditions

The default configuration contains the following scenario flags:

1. `none`
2. `missing_metadata`
3. `ambiguous_mapping`
4. `unit_mismatch`
5. `ontology_service_down`
6. `opcua_endpoint_down`
7. `authentication_failure`
8. `high_load`
9. `secure_and_semantic`
10. `multi_constraint_mixed`

These conditions are benchmark constructs intended to exercise controlled behavior. They should not be interpreted as complete models of all industrial failures or attack modes.

## Measurement categories

The repository contains instrumentation and analysis for:

- latency and percentile latency;
- throughput;
- CPU and memory usage;
- payload and network-related measurements;
- scale sensitivity;
- security overhead;
- robustness degradation;
- recovery-oriented outcomes;
- ablation effects;
- confidence intervals;
- pairwise effect sizes;
- multi-objective Pareto trade-offs.

Not every metric is necessarily applicable to every scenario. Reports should identify the exact metric definition and configuration used.

## Repetition and randomness

The default configuration uses 20 repetitions and seed `4242`. Reproducible runs should preserve the configured seed and record the commit SHA and environment. If a study intentionally varies seeds, the seed schedule should be reported explicitly rather than replaced by an undocumented random state.

## Comparison rules

For scientifically meaningful comparisons:

1. Compare strategies under the same workload, scale, security mode, and scenario condition.
2. Preserve the same measurement and warm-up assumptions across compared methods.
3. Do not compare aggregate values produced from different configuration matrices without labeling the difference.
4. Retain raw run outputs when reporting aggregated statistics.
5. Report both performance and robustness trade-offs where relevant rather than selecting only the most favorable metric.

## Adaptive policy interpretation

`adaptive_selection` is intended to choose among interoperability strategies according to the active policy and operating conditions. Policy-specific conclusions should therefore identify both the selected policy and the scenario context.

An adaptive result should not be described as globally optimal unless the experiment explicitly establishes such a claim over the evaluated objective space.

## Standards-related boundary

The repository contains representative IEEE 1451-style, IEC 61499-style, and OPC UA bridge/adaptation components. These are research abstractions used to study interoperability behavior.

The benchmark does **not** claim:

- complete protocol-stack implementation;
- formal standards conformance;
- certification equivalence;
- hardware-in-the-loop validation;
- production deployment assurance.

See [`paper_claim_boundary.md`](paper_claim_boundary.md) and [`protocol_scope.md`](protocol_scope.md) for the repository's explicit claim boundary.

## Statistical reporting

Descriptive statistics, confidence-interval tooling, and effect-size analysis are available in `analysis/`. Formal inferential claims should only be made when the specific statistical test, assumptions, multiple-comparison handling, and sample definition are explicitly documented and supported by the executed experiment.

At minimum, publication-facing results should report:

- number of repetitions;
- seed or seed schedule;
- aggregation method;
- relevant dispersion or interval estimates;
- effect size when comparing methods;
- exact configuration and commit SHA.

## Reproduction

Use the Docker workflow for the most controlled reproduction:

```bash
docker compose up --build
```

Or use the complete local workflow described in [`reproducibility.md`](reproducibility.md).

## Publication reference

Tavakkoli, V., Mohsenzadegan, K., & Kyamakya, K. (2026). *Adaptive Benchmarking of Industrial Semantic Interoperability Strategies under Scale, Security, and Fault Constraints.* Accepted and Presented at the International Workshop on AI and Mathematical Methods for Real-world Impact (AI2M4RI), in conjunction with the 23rd International Conference on Mobile Systems and Pervasive Computing (MobiSPC), Athens, Greece, August 18–20, 2026.
