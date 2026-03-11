from collections import defaultdict
from statistics import mean

from .simple_png import Canvas, PALETTE


def plot_cpu(rows, out='results/figures/figure_10_cpu_usage.png'):
    c = Canvas(1200, 720)
    c.text(40, 20, 'Figure 10: CPU Usage by Method')
    x0, y0, x1, y1 = c.axes()
    methods = sorted({r['method'] for r in rows})
    by = defaultdict(list)
    for r in rows:
        by[r['method']].append(float(r['cpu_percent_avg']))
    vals = [mean(by[m]) for m in methods]
    vmax = max(vals)
    for i, m in enumerate(methods):
        x = x0 + 120 + i * 240
        h = int((vals[i] / (vmax + 1e-9)) * (y0 - y1))
        c.rect(x, y0 - h, x + 120, y0, PALETTE[i])
        c.text(x, y0 + 24, m[:12])
    c.save_png(out)


def plot_memory(rows, out='results/figures/figure_11_memory_usage.png'):
    c = Canvas(1200, 720)
    c.text(40, 20, 'Figure 11: Memory Usage by Method')
    x0, y0, x1, y1 = c.axes()
    methods = sorted({r['method'] for r in rows})
    by = defaultdict(list)
    for r in rows:
        by[r['method']].append(float(r['memory_mb_avg']))
    vals = [mean(by[m]) for m in methods]
    vmax = max(vals)
    for i, m in enumerate(methods):
        x = x0 + 120 + i * 240
        h = int((vals[i] / (vmax + 1e-9)) * (y0 - y1))
        c.rect(x, y0 - h, x + 120, y0, PALETTE[i])
        c.text(x, y0 + 24, m[:12])
    c.save_png(out)
