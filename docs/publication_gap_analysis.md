# Publication Gap Analysis

| Metric | Current implementation | Problem | Publication risk | Proposed fix | File(s) affected |
|---|---|---|---|---|---|
| Throughput | Derived from wrapper test summaries and scale heuristics | Not measured per independent trial | Inflated/irreproducible performance claims | Measure completed messages / elapsed wall time per run and export raw JSON | `src/compute_metrics.py`, `benchmarks/run_trial.py` |
| Latency | Averaged from mixed scenario tests with ad-hoc scale bins | No p50/p95/p99 per run; not fully traceable | Reviewer cannot verify distributions | Capture per-message timestamps and compute quantiles per run | `src/compute_metrics.py`, `benchmarks/run_trial.py` |
| Startup time | Not measured directly | Startup overhead hidden | Overstates deployability | Add startup profiler around real initializer | `metrics/startup_profiler.py`, `benchmarks/run_trial.py` |
| Payload/message size | Set to zero/default in missing metrics | Non-measured placeholder | Invalid communication-overhead claims | Compute from serialized payload bytes | `src/compute_metrics.py`, `metrics/payload_size.py` |
| CPU usage | Set to zero/default in missing metrics | Placeholder not measured | Invalid resource-usage results | Sample CPU during runs via psutil | `src/compute_metrics.py`, `metrics/resource_monitor.py` |
| Memory usage | Set to zero/default in missing metrics | Placeholder not measured | Invalid resource-usage results | Sample RSS memory during runs via psutil | `src/compute_metrics.py`, `metrics/resource_monitor.py` |
| Network usage | Not measured | Missing systems-level cost | Incomplete benchmark evidence | Record net-io deltas and payload bytes; document approximation limits | `metrics/network_monitor.py`, `benchmarks/run_trial.py` |
| Scalability | Extrapolated from small sensor counts | Extrapolation not execution-backed | Invalid large-scale claims | Run explicit small/medium/large workloads in scenario matrix | `src/compute_metrics.py`, `benchmarks/scenario_matrix.py` |
| Security overhead | Represented by static penalties/defaults | Not measured from executed paths | Can bias conclusions | Measure latency/throughput under explicit security modes | `benchmarks/scenario_matrix.py`, `benchmarks/run_trial.py` |
| Robustness/fault tolerance | Not in benchmark pipeline | No controlled failure evidence | Weak engineering credibility | Add fault injection scenarios and measured recovery metrics | `benchmarks/fault_injection.py`, `benchmarks/robustness_runner.py` |
| Statistical significance | No end-to-end scriptable statistical testing | Reporting risk without assumptions checks | Potentially invalid significance claims | Add assumptions checks, ANOVA/Kruskal, posthoc tests | `analysis/stats_analysis.py` |
| Confidence intervals | Not exported from repeated raw runs | No uncertainty quantification provenance | Overconfident reporting | Compute and export 95% CI from trial-level data | `analysis/aggregate_results.py` |
| Effect sizes | Not computed | Significance-only reporting insufficient | Reduced scientific rigor | Export pairwise Cohen's d | `analysis/effect_sizes.py` |
| Report tables/figures provenance | Existing plots not linked to raw files | Weak traceability | Hard to audit claims | Add manifest and figure-table provenance mapping | `analysis/generate_report.py`, `scripts/run_all.py` |
| Manual post-processing dependence | Prototype scripts require manual assembly | Non-reproducible paper workflow | Fails reproducibility standards | Single orchestration entrypoint for Docker and local | `scripts/run_all.py`, `docker-compose.yml` |
