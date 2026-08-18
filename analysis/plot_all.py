from pathlib import Path


def _fallback_generate(fig_dir: Path):
    """Generate lightweight placeholders only when plotting dependencies are unavailable."""
    from .simple_png import Canvas

    names = [
        'figure_01_experiment_matrix.png', 'figure_02_latency_distribution.png', 'figure_03_latency_p95_comparison.png',
        'figure_04_throughput_comparison.png', 'figure_05_throughput_vs_scale.png', 'figure_06_scalability_latency.png',
        'figure_07_scalability_resources.png', 'figure_08_security_latency_overhead.png', 'figure_09_security_throughput_overhead.png',
        'figure_10_cpu_usage.png', 'figure_11_memory_usage.png', 'figure_12_ablation_impact_latency.png',
        'figure_13_ablation_impact_throughput.png', 'figure_14_robustness_degradation.png', 'figure_15_recovery_success.png',
        'figure_16_confidence_intervals.png', 'figure_17_effect_sizes.png', 'figure_18_pareto_tradeoff.png',
    ]
    for name in names:
        c = Canvas(1000, 600)
        c.rect(50, 50, 950, 550, (230, 235, 245), fill=True)
        c.save_png(str(fig_dir / name))


def plot_all(rows):
    fig_dir = Path('results/figures')
    fig_dir.mkdir(parents=True, exist_ok=True)

    try:
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
    except ImportError:
        # Keep the dependency-free fallback for constrained environments, but do
        # not hide real plotting/API errors behind placeholder figures.
        _fallback_generate(fig_dir)
        return

    plots = [
        ('figure_01_experiment_matrix', plot_experiment_matrix, (rows,)),
        ('figure_02_latency_distribution', plot_latency_distribution, (rows,)),
        ('figure_03_latency_p95_comparison', plot_latency_p95, (rows,)),
        ('figure_04_throughput_comparison', plot_throughput_comparison, (rows,)),
        ('figure_05_throughput_vs_scale', plot_throughput_vs_scale, (rows,)),
        ('figure_06_scalability_latency', plot_scalability_latency, (rows,)),
        ('figure_07_scalability_resources', plot_scalability_resources, (rows,)),
        ('figure_08_security_latency_overhead', plot_security_latency, (rows,)),
        ('figure_09_security_throughput_overhead', plot_security_throughput, (rows,)),
        ('figure_10_cpu_usage', plot_cpu, (rows,)),
        ('figure_11_memory_usage', plot_memory, (rows,)),
        ('figure_12_ablation_impact_latency', plot_ablation_latency, ()),
        ('figure_13_ablation_impact_throughput', plot_ablation_throughput, ()),
        ('figure_14_robustness_degradation', plot_robustness_degradation, ()),
        ('figure_15_recovery_success', plot_recovery_success, ()),
        ('figure_16_confidence_intervals', plot_confidence_intervals, ()),
        ('figure_17_effect_sizes', plot_effect_sizes, ()),
        ('figure_18_pareto_tradeoff', plot_pareto, (rows,)),
    ]

    for figure_name, func, args in plots:
        try:
            func(*args)
        except Exception as exc:
            raise RuntimeError(
                f"Failed to generate {figure_name} with {func.__module__}.{func.__name__}: {exc}"
            ) from exc
