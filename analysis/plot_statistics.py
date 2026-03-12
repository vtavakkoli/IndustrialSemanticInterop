import csv

from .mpl_config import setup_matplotlib

setup_matplotlib()

import matplotlib.pyplot as plt


def _read_csv(path):
    with open(path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def plot_confidence_intervals(ci_csv='results/aggregated/confidence_intervals.csv', out='results/figures/figure_16_confidence_intervals.png'):
    rows = _read_csv(ci_csv)
    labels = [f"{r['method']}|{r['scale']}" for r in rows]
    means = [float(r['mean']) for r in rows]
    low = [float(r['ci95_low']) for r in rows]
    high = [float(r['ci95_high']) for r in rows]
    yerr = [[m - l for m, l in zip(means, low)], [h - m for m, h in zip(means, high)]]

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.errorbar(range(len(labels)), means, yerr=yerr, fmt='o', capsize=4)
    ax.set_title('Figure 16: Latency Mean with 95% Confidence Intervals')
    ax.set_xlabel('Method | Scale')
    ax.set_ylabel('Latency (ms)')
    ax.set_xticks(range(len(labels)), labels, rotation=35, ha='right')
    ax.grid(axis='y', alpha=0.3)
    plt.savefig(out)
    plt.close(fig)


def plot_effect_sizes(effect_csv='results/aggregated/effect_sizes.csv', out='results/figures/figure_17_effect_sizes.png'):
    rows = _read_csv(effect_csv)
    labels = [f"{r['method_a']}→{r['method_b']}\n({r['scale']})" for r in rows]
    vals = [float(r['mean_diff_ms']) for r in rows]

    fig, ax = plt.subplots(figsize=(12, 7))
    colors = ['#d62728' if v > 0 else '#2ca02c' for v in vals]
    ax.bar(range(len(vals)), vals, color=colors)
    ax.axhline(0, color='black', linewidth=1)
    ax.set_title('Figure 17: Effect Sizes (Mean Latency Differences)')
    ax.set_xlabel('Method pair')
    ax.set_ylabel('Δ latency (ms)')
    ax.set_xticks(range(len(labels)), labels, rotation=35, ha='right')
    ax.grid(axis='y', alpha=0.3)
    plt.savefig(out)
    plt.close(fig)
