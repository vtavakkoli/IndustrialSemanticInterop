from collections import defaultdict
from statistics import mean
from ._simple_plot import write_svg_bar


def plot_scalability(rows, out="results/figures/scalability.svg"):
    g = defaultdict(list)
    for r in rows:
        g[(r['method'], r['scale'])].append(r['latency_p95_ms'])
    labels, vals = [], []
    for k, v in sorted(g.items()):
        labels.append(f"{k[0]}|{k[1]}")
        vals.append(mean(v))
    write_svg_bar(out, "P95 latency by scale", labels, vals, "ms")
