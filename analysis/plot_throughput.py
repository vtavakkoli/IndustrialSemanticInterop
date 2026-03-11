from collections import defaultdict
from statistics import mean

from .simple_png import Canvas, PALETTE


def plot_throughput_comparison(rows, out='results/figures/figure_04_throughput_comparison.png'):
    c = Canvas(1200, 720)
    c.text(40, 20, 'Figure 04: Throughput by Method and Security Mode')
    x0, y0, x1, y1 = c.axes()
    methods = sorted({r['method'] for r in rows})
    sec = ['none', 'auth', 'encryption', 'full']
    by = defaultdict(list)
    for r in rows:
        by[(r['method'], r['security'])].append(float(r['throughput_msg_per_sec']))
    vals = [mean(v) for v in by.values()]
    vmin, vmax = min(vals), max(vals)
    gw = (x1 - x0 - 40) // len(methods)
    for mi, m in enumerate(methods):
        for si, s in enumerate(sec):
            v = mean(by[(m, s)])
            h = int((v - vmin) / (vmax - vmin + 1e-9) * (y0 - y1))
            x = x0 + mi * gw + si * max(10, gw // len(sec) - 6)
            w = max(8, gw // len(sec) - 10)
            c.rect(x + 15, y0 - h, x + 15 + w, y0, PALETTE[si % len(PALETTE)])
        c.text(x0 + mi * gw + 20, y0 + 24, m[:14])
    c.text(40, 680, 'Per-method bars show security overhead impact on message throughput.')
    c.save_png(out)


def plot_throughput_vs_scale(rows, out='results/figures/figure_05_throughput_vs_scale.png'):
    c = Canvas(1200, 720)
    c.text(40, 20, 'Figure 05: Throughput vs Scale')
    x0, y0, x1, y1 = c.axes()
    methods = sorted({r['method'] for r in rows})
    scales = ['small', 'medium', 'large']
    pos = {'small': x0 + 120, 'medium': (x0 + x1) // 2, 'large': x1 - 120}
    by = defaultdict(list)
    for r in rows:
        by[(r['method'], r['scale'])].append(float(r['throughput_msg_per_sec']))
    vals = [mean(v) for v in by.values()]
    vmin, vmax = min(vals), max(vals)
    for mi, m in enumerate(methods):
        pts = []
        for s in scales:
            v = mean(by[(m, s)])
            y = int(y0 - (v - vmin) / (vmax - vmin + 1e-9) * (y0 - y1))
            x = pos[s] + (mi - 1) * 10
            pts.append((x, y))
            c.circle(x, y, 4, PALETTE[mi % len(PALETTE)])
        for p0, p1 in zip(pts, pts[1:]):
            c.line(p0[0], p0[1], p1[0], p1[1], PALETTE[mi % len(PALETTE)], 2)
        c.text(x1 - 220, 80 + mi * 16, m)
    for s, x in pos.items():
        c.text(x - 20, y0 + 24, s)
    c.save_png(out)
