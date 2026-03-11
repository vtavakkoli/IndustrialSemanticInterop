from collections import defaultdict
from statistics import mean

from .simple_png import Canvas, PALETTE


def plot_security_latency(rows, out='results/figures/figure_08_security_latency_overhead.png'):
    c = Canvas(1200, 720)
    c.text(40, 20, 'Figure 08: Security Latency Overhead')
    x0, y0, x1, y1 = c.axes()
    sec = ['none', 'auth', 'encryption', 'full']
    by = defaultdict(list)
    for r in rows:
        by[r['security']].append(float(r['latency_mean_ms']))
    vals = [mean(by[s]) for s in sec]
    vmax = max(vals)
    for i, s in enumerate(sec):
        x = x0 + 60 + i * 220
        h = int((vals[i] / (vmax + 1e-9)) * (y0 - y1))
        c.rect(x, y0 - h, x + 120, y0, PALETTE[i])
        c.text(x, y0 + 24, s)
    c.save_png(out)


def plot_security_throughput(rows, out='results/figures/figure_09_security_throughput_overhead.png'):
    c = Canvas(1200, 720)
    c.text(40, 20, 'Figure 09: Security Throughput Overhead')
    x0, y0, x1, y1 = c.axes()
    sec = ['none', 'auth', 'encryption', 'full']
    by = defaultdict(list)
    for r in rows:
        by[r['security']].append(float(r['throughput_msg_per_sec']))
    vals = [mean(by[s]) for s in sec]
    vmax = max(vals)
    for i, s in enumerate(sec):
        x = x0 + 60 + i * 220
        h = int((vals[i] / (vmax + 1e-9)) * (y0 - y1))
        c.rect(x, y0 - h, x + 120, y0, PALETTE[i])
        c.text(x, y0 + 24, s)
    c.save_png(out)
