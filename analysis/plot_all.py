from pathlib import Path
from .plot_latency import plot_latency
from .plot_throughput import plot_throughput
from .plot_scalability import plot_scalability
from .plot_security_overhead import plot_security_overhead
from .plot_ablations import plot_ablations
from .plot_robustness import plot_robustness
from .plot_pareto import plot_pareto


def plot_all(df):
    Path("results/figures").mkdir(parents=True, exist_ok=True)
    plot_latency(df)
    plot_throughput(df)
    plot_scalability(df)
    plot_security_overhead(df)
    plot_ablations()
    plot_robustness()
    plot_pareto(df)
