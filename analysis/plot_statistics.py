import csv
from pathlib import Path
from collections import defaultdict

from .simple_png import Canvas, PALETTE


def _read_csv(path):
    with open(path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def plot_confidence_intervals(ci_csv='results/aggregated/confidence_intervals.csv', out='results/figures/figure_16_confidence_intervals.png'):
    rows = _read_csv(ci_csv)
    c = Canvas(1200, 720)
    c.text(40, 20, 'Figure 16: 95% Confidence Intervals (Latency Mean)')
    x0, y0, x1, y1 = c.axes()
    methods = sorted({r['method'] for r in rows})
    vals = [(float(r['ci95_low']), float(r['mean']), float(r['ci95_high'])) for r in rows]
    vmin = min(v[0] for v in vals)
    vmax = max(v[2] for v in vals)
    step = max(80, (x1 - x0 - 60) // max(1, len(rows)))
    for i, r in enumerate(rows):
        lo, mid, hi = float(r['ci95_low']), float(r['mean']), float(r['ci95_high'])
        sy = lambda v: int(y0 - (v - vmin) / (vmax - vmin + 1e-9) * (y0 - y1))
        x = x0 + 30 + i * step
        c.line(x, sy(lo), x, sy(hi), (40,40,40), 2)
        c.circle(x, sy(mid), 4, PALETTE[i % len(PALETTE)])
        c.text(x - 8, y0 + 24, r['method'][:7])
    c.save_png(out)


def plot_effect_sizes(effect_csv='results/aggregated/effect_sizes.csv', out='results/figures/figure_17_effect_sizes.png'):
    rows = _read_csv(effect_csv)
    c = Canvas(1200, 720)
    c.text(40, 20, 'Figure 17: Pairwise Effect Sizes (Mean Latency Difference)')
    x0, y0, x1, y1 = c.axes()
    vals = [float(r['mean_diff_ms']) for r in rows] or [0.0]
    vmin, vmax = min(vals), max(vals)
    step = max(60, (x1 - x0 - 80) // max(1, len(rows)))
    for i, r in enumerate(rows):
        v = float(r['mean_diff_ms'])
        y = int(y0 - (v - vmin) / (vmax - vmin + 1e-9) * (y0 - y1))
        x = x0 + 40 + i * step
        c.circle(x, y, 5, PALETTE[i % len(PALETTE)])
        c.text(x - 10, y0 + 24, f"{r['method_a'][:3]}-{r['method_b'][:3]}")
    c.save_png(out)
