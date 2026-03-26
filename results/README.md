# Generated Results

This directory is intentionally excluded from version control for large/binary reproducible artifacts.

To regenerate the full benchmark outputs (including Figures 12–15 and final reports):

```bash
PYTHONPATH=. python scripts/run_all.py
```

Key generated artifacts:
- `results/figures/figure_12_ablation_impact_latency.{png,svg}`
- `results/figures/figure_13_ablation_impact_throughput.{png,svg}`
- `results/figures/figure_14_robustness_degradation.{png,svg}`
- `results/figures/figure_15_recovery_success.{png,svg}`
- `results/final_report.html`
- `results/final_report.md`
