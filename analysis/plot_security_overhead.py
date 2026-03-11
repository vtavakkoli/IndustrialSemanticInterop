from collections import defaultdict
from statistics import mean
from ._simple_plot import write_svg_bar


def plot_security_overhead(rows, out="results/figures/security_overhead.svg"):
    g = defaultdict(list)
    for r in rows:
        g[r['security']].append(r['latency_mean_ms'])
    labels = sorted(g)
    vals = [mean(g[k]) for k in labels]
    write_svg_bar(out, "Security overhead (latency)", labels, vals, "ms")
