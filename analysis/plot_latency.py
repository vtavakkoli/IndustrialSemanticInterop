from collections import defaultdict
from statistics import mean

from .simple_png import Canvas, PALETTE, GRID


def _group(rows, key):
    g = defaultdict(list)
    for r in rows:
        g[r[key]].append(float(r['latency_mean_ms']))
    return g


def plot_latency_distribution(rows, out='results/figures/figure_02_latency_distribution.png'):
    c = Canvas(1200, 720)
    c.text(40, 20, 'Figure 02: Latency Distribution by Method')
    x0, y0, x1, y1 = c.axes()
    g = _group(rows, 'method')
    methods = sorted(g)
    all_vals = [v for vs in g.values() for v in vs]
    vmin, vmax = min(all_vals), max(all_vals)
    bw = (x1 - x0 - 60) // max(1, len(methods))
    for i, m in enumerate(methods):
        vals = sorted(g[m])
        p25 = vals[int(0.25 * (len(vals)-1))]
        p50 = vals[int(0.50 * (len(vals)-1))]
        p75 = vals[int(0.75 * (len(vals)-1))]
        p95 = vals[int(0.95 * (len(vals)-1))]
        lo, hi = vals[0], vals[-1]
        def sy(v):
            return int(y0 - (v - vmin) / (vmax - vmin + 1e-9) * (y0 - y1))
        x = x0 + 30 + i * bw
        c.line(x + bw//2, sy(lo), x + bw//2, sy(hi), (100,100,100), 2)
        c.rect(x + 10, sy(p75), x + bw - 10, sy(p25), PALETTE[i % len(PALETTE)])
        c.line(x + 10, sy(p50), x + bw - 10, sy(p50), (255,255,255), 2)
        c.line(x + 14, sy(p95), x + bw - 14, sy(p95), (220,40,40), 2)
        c.text(x + 8, y0 + 20, m[:14])
    c.text(40, 680, 'Box = IQR, white line = median, red line = p95, whiskers = min/max latency.')
    c.save_png(out)


def plot_latency_p95(rows, out='results/figures/figure_03_latency_p95_comparison.png'):
    c = Canvas(1200, 720)
    c.text(40, 20, 'Figure 03: P95 Latency by Method and Scale')
    x0, y0, x1, y1 = c.axes()
    scales = ['small', 'medium', 'large']
    methods = sorted({r['method'] for r in rows})
    by = defaultdict(list)
    for r in rows:
        by[(r['method'], r['scale'])].append(float(r['latency_p95_ms']))
    vals = [mean(v) for v in by.values()]
    vmin, vmax = min(vals), max(vals)
    gw = (x1 - x0 - 50) // len(scales)
    for si, s in enumerate(scales):
        for mi, m in enumerate(methods):
            v = mean(by[(m, s)])
            h = int((v - vmin) / (vmax - vmin + 1e-9) * (y0 - y1))
            x = x0 + 20 + si * gw + mi * (gw // len(methods))
            w = max(12, gw // len(methods) - 8)
            c.rect(x, y0 - h, x + w, y0, PALETTE[mi % len(PALETTE)])
            if mi == 0:
                c.text(x0 + 20 + si * gw, y0 + 24, s)
    c.text(40, 680, 'Higher bars indicate heavier tail latency (p95).')
    c.save_png(out)
