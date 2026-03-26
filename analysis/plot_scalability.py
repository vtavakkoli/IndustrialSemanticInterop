from collections import defaultdict

from .mpl_config import setup_matplotlib

setup_matplotlib()

import matplotlib.pyplot as plt


def plot_scalability_latency(rows, out='results/figures/figure_06_scalability_latency.png'):
    methods = sorted({r['method'] for r in rows})
    scales = ['small', 'medium', 'large']
    vals = defaultdict(list)
    for r in rows:
        vals[(r['method'], r['scale'])].append(float(r['latency_mean_ms']))

    fig, ax = plt.subplots(figsize=(11, 7))
    for m in methods:
        ys = [sum(vals[(m, s)]) / max(1, len(vals[(m, s)])) for s in scales]
        ax.plot(scales, ys, marker='o', linewidth=2, label=m)
    ax.set_title('Figure 06: Scalability - Latency vs Scale')
    ax.set_xlabel('Scale')
    ax.set_ylabel('Latency (ms)')
    ax.legend(title='Method')
    ax.grid(alpha=0.3)
    plt.savefig(out)
    plt.close(fig)


def plot_scalability_resources(rows, out='results/figures/figure_07_scalability_resources.png'):
    scales = ['small', 'medium', 'large']
    cpu = defaultdict(list)
    mem = defaultdict(list)
    for r in rows:
        cpu[r['scale']].append(float(r['cpu_percent_avg']))
        mem[r['scale']].append(float(r['memory_mb_avg']))
    cpu_y = [sum(cpu[s]) / max(1, len(cpu[s])) for s in scales]
    mem_y = [sum(mem[s]) / max(1, len(mem[s])) for s in scales]

    fig, ax1 = plt.subplots(figsize=(11, 7))
    x = range(len(scales))
    ax1.plot(x, cpu_y, marker='o', color='tab:blue', label='CPU usage')
    ax1.set_ylabel('CPU usage (load proxy)', color='tab:blue')
    ax1.tick_params(axis='y', labelcolor='tab:blue')
    ax1.set_xticks(list(x), scales)

    ax2 = ax1.twinx()
    ax2.plot(x, mem_y, marker='s', color='tab:orange', label='Memory usage')
    ax2.set_ylabel('Memory (MB)', color='tab:orange')
    ax2.tick_params(axis='y', labelcolor='tab:orange')

    ax1.set_title('Figure 07: Scalability - CPU and Memory vs Scale')
    ax1.set_xlabel('Scale')
    plt.savefig(out)
    plt.close(fig)
