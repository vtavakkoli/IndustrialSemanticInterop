from collections import defaultdict

from .mpl_config import setup_matplotlib

setup_matplotlib()

import matplotlib.pyplot as plt


def plot_pareto(rows, out='results/figures/figure_18_pareto_tradeoff.png'):
    vals = defaultdict(list)
    for r in rows:
        vals[r['method']].append(r)

    fig, ax = plt.subplots(figsize=(11, 7))
    for method, rs in sorted(vals.items()):
        lat = sum(float(r['latency_mean_ms']) for r in rs) / len(rs)
        thr = sum(float(r['throughput_msg_per_sec']) for r in rs) / len(rs)
        mem = sum(float(r['memory_mb_avg']) for r in rs) / len(rs)
        ax.scatter(lat, thr, s=max(50, mem * 12), alpha=0.7, label=method)
        ax.annotate(method, (lat, thr), textcoords='offset points', xytext=(5, 5))

    ax.set_title('Figure 18: Pareto Tradeoff (Latency vs Throughput, bubble=memory)')
    ax.set_xlabel('Latency (ms, lower is better)')
    ax.set_ylabel('Throughput (msg/s, higher is better)')
    ax.legend(title='Method')
    ax.grid(alpha=0.3)
    plt.savefig(out)
    plt.close(fig)
