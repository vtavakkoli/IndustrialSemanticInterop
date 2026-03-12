from pathlib import Path
import json
from collections import defaultdict

from .mpl_config import setup_matplotlib

setup_matplotlib()

import matplotlib.pyplot as plt


def _rows(path='results/ablations'):
    return [json.loads(p.read_text()) for p in sorted(Path(path).glob('*.json'))]


def plot_ablation_latency(path='results/ablations', out='results/figures/figure_12_ablation_impact_latency.png'):
    rows = _rows(path)
    vals = defaultdict(list)
    for r in rows:
        key = 'reasoning_on' if r.get('ablation', {}).get('reasoning', True) else 'reasoning_off'
        vals[key].append(float(r['latency_mean_ms']))
    labels = sorted(vals)
    ys = [sum(vals[k]) / max(1, len(vals[k])) for k in labels]

    fig, ax = plt.subplots(figsize=(11, 7))
    ax.bar(labels, ys, color=['#1f77b4', '#ff7f0e'])
    ax.set_title('Figure 12: Ablation Impact on Latency')
    ax.set_xlabel('Ablation setting')
    ax.set_ylabel('Latency (ms)')
    ax.grid(axis='y', alpha=0.3)
    plt.savefig(out)
    plt.close(fig)


def plot_ablation_throughput(path='results/ablations', out='results/figures/figure_13_ablation_impact_throughput.png'):
    rows = _rows(path)
    vals = defaultdict(list)
    for r in rows:
        key = 'cache_on' if r.get('ablation', {}).get('cache', True) else 'cache_off'
        vals[key].append(float(r['throughput_msg_per_sec']))
    labels = sorted(vals)
    ys = [sum(vals[k]) / max(1, len(vals[k])) for k in labels]

    fig, ax = plt.subplots(figsize=(11, 7))
    ax.bar(labels, ys, color=['#2ca02c', '#d62728'])
    ax.set_title('Figure 13: Ablation Impact on Throughput')
    ax.set_xlabel('Ablation setting')
    ax.set_ylabel('Throughput (msg/s)')
    ax.grid(axis='y', alpha=0.3)
    plt.savefig(out)
    plt.close(fig)
