from collections import defaultdict
from statistics import mean

from .simple_png import Canvas, PALETTE


def plot_scalability_latency(rows, out='results/figures/figure_06_scalability_latency.png'):
    c = Canvas(1200, 720)
    c.text(40, 20, 'Figure 06: Scalability - Latency vs Scale')
    x0, y0, x1, y1 = c.axes()
    methods = sorted({r['method'] for r in rows})
    scales = ['small', 'medium', 'large']
    pos = {'small': x0 + 120, 'medium': (x0 + x1) // 2, 'large': x1 - 120}
    by = defaultdict(list)
    for r in rows:
        by[(r['method'], r['scale'])].append(float(r['latency_mean_ms']))
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
        for a, b in zip(pts, pts[1:]):
            c.line(a[0], a[1], b[0], b[1], PALETTE[mi % len(PALETTE)], 2)
    for s, x in pos.items():
        c.text(x - 20, y0 + 24, s)
    c.save_png(out)


def plot_scalability_resources(rows, out='results/figures/figure_07_scalability_resources.png'):
    c = Canvas(1200, 720)
    c.text(40, 20, 'Figure 07: Scalability - CPU/Memory vs Scale')
    x0, y0, x1, y1 = c.axes()
    scales = ['small', 'medium', 'large']
    cpu = defaultdict(list)
    mem = defaultdict(list)
    for r in rows:
        cpu[r['scale']].append(float(r['cpu_percent_avg']))
        mem[r['scale']].append(float(r['memory_mb_avg']))
    cvals = [mean(cpu[s]) for s in scales]
    mvals = [mean(mem[s]) for s in scales]
    vmax = max(max(cvals), max(mvals))
    for i, s in enumerate(scales):
        x = x0 + 150 + i * 260
        ch = int((cvals[i] / (vmax + 1e-9)) * (y0 - y1))
        mh = int((mvals[i] / (vmax + 1e-9)) * (y0 - y1))
        c.rect(x, y0 - ch, x + 50, y0, (76,120,168))
        c.rect(x + 60, y0 - mh, x + 110, y0, (245,133,24))
        c.text(x, y0 + 24, s)
    c.text(40, 680, 'Blue=CPU(load proxy), Orange=Memory(MB).')
    c.save_png(out)
