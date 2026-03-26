from collections import defaultdict

from .mpl_config import setup_matplotlib

setup_matplotlib()

import matplotlib.pyplot as plt


def plot_throughput_comparison(rows, out='results/figures/figure_04_throughput_comparison.png'):
    methods = sorted({r['method'] for r in rows})
    sec = ['none', 'auth', 'encryption', 'full']
    vals = defaultdict(list)
    for r in rows:
        vals[(r['method'], r['security'])].append(float(r['throughput_msg_per_sec']))

    fig, ax = plt.subplots(figsize=(11, 7))
    width = 0.18
    xs = list(range(len(methods)))
    for j, s in enumerate(sec):
        ys = [sum(vals[(m, s)]) / max(1, len(vals[(m, s)])) for m in methods]
        pos = [x + (j - 1.5) * width for x in xs]
        ax.bar(pos, ys, width, label=s)
    ax.set_xticks(xs, methods)
    ax.set_title('Figure 04: Throughput Comparison by Method and Security')
    ax.set_xlabel('Method')
    ax.set_ylabel('Throughput (msg/s)')
    ax.legend(title='Security')
    ax.grid(axis='y', alpha=0.3)
    plt.savefig(out)
    plt.close(fig)


def plot_throughput_vs_scale(rows, out='results/figures/figure_05_throughput_vs_scale.png'):
    methods = sorted({r['method'] for r in rows})
    scales = ['small', 'medium', 'large']
    vals = defaultdict(list)
    for r in rows:
        vals[(r['method'], r['scale'])].append(float(r['throughput_msg_per_sec']))

    fig, ax = plt.subplots(figsize=(11, 7))
    for m in methods:
        ys = [sum(vals[(m, s)]) / max(1, len(vals[(m, s)])) for s in scales]
        ax.plot(scales, ys, marker='o', linewidth=2, label=m)
    ax.set_title('Figure 05: Throughput vs Scale')
    ax.set_xlabel('Scale')
    ax.set_ylabel('Throughput (msg/s)')
    ax.legend(title='Method')
    ax.grid(alpha=0.3)
    plt.savefig(out)
    plt.close(fig)
