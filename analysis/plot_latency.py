from collections import defaultdict

from .mpl_config import setup_matplotlib

setup_matplotlib()

import matplotlib.pyplot as plt


def plot_latency_distribution(rows, out='results/figures/figure_02_latency_distribution.png'):
    methods = sorted({r['method'] for r in rows})
    data = [[float(r['latency_mean_ms']) for r in rows if r['method'] == m] for m in methods]
    fig, ax = plt.subplots(figsize=(11, 7))
    bp = ax.boxplot(data, labels=methods, patch_artist=True, showmeans=True)
    for patch in bp['boxes']:
        patch.set_facecolor('#a6cee3')
    ax.set_title('Figure 02: Latency Distribution by Method')
    ax.set_xlabel('Method')
    ax.set_ylabel('Latency (ms)')
    ax.grid(axis='y', alpha=0.3)
    plt.savefig(out)
    plt.close(fig)


def plot_latency_p95(rows, out='results/figures/figure_03_latency_p95_comparison.png'):
    methods = sorted({r['method'] for r in rows})
    scales = ['small', 'medium', 'large']
    vals = defaultdict(list)
    for r in rows:
        vals[(r['method'], r['scale'])].append(float(r['latency_p95_ms']))
    fig, ax = plt.subplots(figsize=(11, 7))
    width = 0.25
    xs = list(range(len(scales)))
    for i, m in enumerate(methods):
        ys = [sum(vals[(m, s)]) / max(1, len(vals[(m, s)])) for s in scales]
        pos = [x + (i - 1) * width for x in xs]
        ax.bar(pos, ys, width=width, label=m)
    ax.set_xticks(xs, scales)
    ax.set_title('Figure 03: P95 Latency Comparison by Scale')
    ax.set_xlabel('Scale')
    ax.set_ylabel('P95 latency (ms)')
    ax.legend(title='Method')
    ax.grid(axis='y', alpha=0.3)
    plt.savefig(out)
    plt.close(fig)
