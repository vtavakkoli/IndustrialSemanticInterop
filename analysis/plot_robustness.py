from pathlib import Path
import json
from collections import defaultdict

from .mpl_config import setup_matplotlib

setup_matplotlib()

import matplotlib.pyplot as plt


def _rows(path='results/robustness'):
    return [json.loads(p.read_text()) for p in sorted(Path(path).glob('*.json'))]


def plot_robustness_degradation(path='results/robustness', out='results/figures/figure_14_robustness_degradation.png'):
    rows = _rows(path)
    vals = defaultdict(list)
    for r in rows:
        vals[r['notes'].replace('fault=', '')].append(float(r['failure_rate']))
    labels = sorted(vals)
    ys = [sum(vals[k]) / max(1, len(vals[k])) for k in labels]

    fig, ax = plt.subplots(figsize=(11, 7))
    ax.bar(labels, ys, color='#9467bd')
    ax.set_title('Figure 14: Robustness Degradation under Faults')
    ax.set_xlabel('Fault type')
    ax.set_ylabel('Failure rate')
    ax.tick_params(axis='x', rotation=25)
    ax.grid(axis='y', alpha=0.3)
    plt.savefig(out)
    plt.close(fig)


def plot_recovery_success(path='results/robustness', out='results/figures/figure_15_recovery_success.png'):
    rows = _rows(path)
    vals = defaultdict(list)
    for r in rows:
        vals[r['notes'].replace('fault=', '')].append(float(r['retry_success_rate']))
    labels = sorted(vals)
    ys = [sum(vals[k]) / max(1, len(vals[k])) for k in labels]

    fig, ax = plt.subplots(figsize=(11, 7))
    ax.bar(labels, ys, color='#17becf')
    ax.set_title('Figure 15: Recovery Success Rate by Fault')
    ax.set_xlabel('Fault type')
    ax.set_ylabel('Retry success rate')
    ax.tick_params(axis='x', rotation=25)
    ax.grid(axis='y', alpha=0.3)
    plt.savefig(out)
    plt.close(fig)
