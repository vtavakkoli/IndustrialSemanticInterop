from pathlib import Path

from .plot_experiment_matrix import plot_experiment_matrix
from .plot_latency import plot_latency_distribution, plot_latency_p95
from .plot_throughput import plot_throughput_comparison, plot_throughput_vs_scale
from .plot_scalability import plot_scalability_latency, plot_scalability_resources
from .plot_security_overhead import plot_security_latency, plot_security_throughput
from .plot_resources import plot_cpu, plot_memory
from .plot_ablations import plot_ablation_latency, plot_ablation_throughput
from .plot_robustness import plot_robustness_degradation, plot_recovery_success
from .plot_statistics import plot_confidence_intervals, plot_effect_sizes
from .plot_pareto import plot_pareto


def plot_all(rows):
    Path('results/figures').mkdir(parents=True, exist_ok=True)
    plot_experiment_matrix(rows)
    plot_latency_distribution(rows)
    plot_latency_p95(rows)
    plot_throughput_comparison(rows)
    plot_throughput_vs_scale(rows)
    plot_scalability_latency(rows)
    plot_scalability_resources(rows)
    plot_security_latency(rows)
    plot_security_throughput(rows)
    plot_cpu(rows)
    plot_memory(rows)
    plot_ablation_latency()
    plot_ablation_throughput()
    plot_robustness_degradation()
    plot_recovery_success()
    plot_confidence_intervals()
    plot_effect_sizes()
    plot_pareto(rows)
