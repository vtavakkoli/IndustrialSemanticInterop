from collections import defaultdict
from statistics import mean

from .simple_png import Canvas, PALETTE


def plot_pareto(rows, out='results/figures/figure_18_pareto_tradeoff.png'):
    c = Canvas(1200, 720)
    c.text(40, 20, 'Figure 18: Pareto Tradeoff (Latency vs Throughput, bubble=memory)')
    x0, y0, x1, y1 = c.axes()
    g = defaultdict(list)
    for r in rows:
        g[r['method']].append(r)
    pts = []
    for m, vals in sorted(g.items()):
        pts.append((m, mean(float(v['latency_mean_ms']) for v in vals), mean(float(v['throughput_msg_per_sec']) for v in vals), mean(float(v['memory_mb_avg']) for v in vals)))
    xs = [p[1] for p in pts] or [0,1]
    ys = [p[2] for p in pts] or [0,1]
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)
    for i, (m, lat, thr, mem) in enumerate(pts):
        x = int(x0 + (lat - xmin) / (xmax - xmin + 1e-9) * (x1 - x0))
        y = int(y0 - (thr - ymin) / (ymax - ymin + 1e-9) * (y0 - y1))
        r = max(4, min(18, int(mem / 2 + 4)))
        c.circle(x, y, r, PALETTE[i % len(PALETTE)], fill=False)
        c.text(x + 8, y - 6, m)
    c.text(40, 680, 'Lower latency (left) and higher throughput (up) are better; larger circles indicate higher memory cost.')
    c.save_png(out)
