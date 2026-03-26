from collections import defaultdict

from .mpl_config import setup_matplotlib

setup_matplotlib()

import matplotlib.pyplot as plt


def plot_cpu(rows, out='results/figures/figure_10_cpu_usage.png'):
    methods = sorted({r['method'] for r in rows})
    vals = defaultdict(list)
    for r in rows:
        vals[r['method']].append(float(r['cpu_percent_avg']))
    ys = [sum(vals[m]) / max(1, len(vals[m])) for m in methods]

    fig, ax = plt.subplots(figsize=(11, 7))
    ax.bar(methods, ys, color='#4c78a8')
    ax.set_title('Figure 10: CPU Usage by Method')
    ax.set_xlabel('Method')
    ax.set_ylabel('CPU usage (load proxy)')
    ax.grid(axis='y', alpha=0.3)
    plt.savefig(out)
    plt.close(fig)


def plot_memory(rows, out='results/figures/figure_11_memory_usage.png'):
    methods = sorted({r['method'] for r in rows})
    vals = defaultdict(list)
    for r in rows:
        vals[r['method']].append(float(r['memory_mb_avg']))
    ys = [sum(vals[m]) / max(1, len(vals[m])) for m in methods]

    fig, ax = plt.subplots(figsize=(11, 7))
    ax.bar(methods, ys, color='#f58518')
    ax.set_title('Figure 11: Memory Usage by Method')
    ax.set_xlabel('Method')
    ax.set_ylabel('Memory (MB)')
    ax.grid(axis='y', alpha=0.3)
    plt.savefig(out)
    plt.close(fig)
