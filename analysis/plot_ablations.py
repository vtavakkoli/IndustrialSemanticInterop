from pathlib import Path
import json
from collections import defaultdict
from statistics import mean

from .simple_png import Canvas, PALETTE


def _rows(path='results/ablations'):
    return [json.loads(p.read_text()) for p in sorted(Path(path).glob('*.json'))]


def plot_ablation_latency(path='results/ablations', out='results/figures/figure_12_ablation_impact_latency.png'):
    rows = _rows(path)
    c = Canvas(1200, 720)
    c.text(40, 20, 'Figure 12: Ablation Impact on Latency')
    x0, y0, x1, y1 = c.axes()
    by = defaultdict(list)
    for r in rows:
        label = 'reasoning_on' if r.get('ablation', {}).get('reasoning', True) else 'reasoning_off'
        by[label].append(float(r['latency_mean_ms']))
    labels = sorted(by)
    vals = [mean(by[l]) for l in labels]
    vmax = max(vals) if vals else 1
    for i, l in enumerate(labels):
        x = x0 + 180 + i * 260
        h = int((vals[i] / vmax) * (y0 - y1))
        c.rect(x, y0 - h, x + 120, y0, PALETTE[i])
        c.text(x, y0 + 24, l)
    c.save_png(out)


def plot_ablation_throughput(path='results/ablations', out='results/figures/figure_13_ablation_impact_throughput.png'):
    rows = _rows(path)
    c = Canvas(1200, 720)
    c.text(40, 20, 'Figure 13: Ablation Impact on Throughput')
    x0, y0, x1, y1 = c.axes()
    by = defaultdict(list)
    for r in rows:
        label = 'cache_on' if r.get('ablation', {}).get('cache', True) else 'cache_off'
        by[label].append(float(r['throughput_msg_per_sec']))
    labels = sorted(by)
    vals = [mean(by[l]) for l in labels]
    vmax = max(vals) if vals else 1
    for i, l in enumerate(labels):
        x = x0 + 180 + i * 260
        h = int((vals[i] / vmax) * (y0 - y1))
        c.rect(x, y0 - h, x + 120, y0, PALETTE[i])
        c.text(x, y0 + 24, l)
    c.save_png(out)
