from pathlib import Path
import json
from collections import defaultdict
from statistics import mean

from .simple_png import Canvas, PALETTE


def _rows(path='results/robustness'):
    return [json.loads(p.read_text()) for p in sorted(Path(path).glob('*.json'))]


def plot_robustness_degradation(path='results/robustness', out='results/figures/figure_14_robustness_degradation.png'):
    rows = _rows(path)
    c = Canvas(1200, 720)
    c.text(40, 20, 'Figure 14: Robustness Degradation (Failure Rate)')
    x0, y0, x1, y1 = c.axes()
    by = defaultdict(list)
    for r in rows:
        by[r['notes'].replace('fault=', '')].append(float(r['failure_rate']))
    labels = sorted(by)
    vals = [mean(by[l]) for l in labels]
    vmax = max(vals) if vals else 1
    step = max(80, (x1 - x0 - 80) // max(1, len(labels)))
    for i, l in enumerate(labels):
        x = x0 + 40 + i * step
        h = int((vals[i] / (vmax + 1e-9)) * (y0 - y1))
        c.rect(x, y0 - h, x + step - 20, y0, PALETTE[i % len(PALETTE)])
        c.text(x, y0 + 24, l[:14])
    c.save_png(out)


def plot_recovery_success(path='results/robustness', out='results/figures/figure_15_recovery_success.png'):
    rows = _rows(path)
    c = Canvas(1200, 720)
    c.text(40, 20, 'Figure 15: Recovery Success Rate by Fault')
    x0, y0, x1, y1 = c.axes()
    by = defaultdict(list)
    for r in rows:
        by[r['notes'].replace('fault=', '')].append(float(r['retry_success_rate']))
    labels = sorted(by)
    vals = [mean(by[l]) for l in labels]
    vmax = max(vals) if vals else 1
    step = max(80, (x1 - x0 - 80) // max(1, len(labels)))
    for i, l in enumerate(labels):
        x = x0 + 40 + i * step
        h = int((vals[i] / (vmax + 1e-9)) * (y0 - y1))
        c.rect(x, y0 - h, x + step - 20, y0, PALETTE[i % len(PALETTE)])
        c.text(x, y0 + 24, l[:14])
    c.save_png(out)
