from collections import defaultdict

from .mpl_config import setup_matplotlib

setup_matplotlib()

import matplotlib.pyplot as plt


def plot_experiment_matrix(rows, out='results/figures/figure_01_experiment_matrix.png'):
    methods = sorted({r['method'] for r in rows})
    scales = ['small', 'medium', 'large']
    security = ['none', 'auth', 'encryption', 'full']
    reps = defaultdict(set)
    for r in rows:
        reps[(r['method'], r['scale'], r['security'])].add(int(r['run_index']))

    matrix = []
    labels = []
    for m in methods:
        for s in scales:
            labels.append(f"{m}\n{s}")
            matrix.append([len(reps[(m, s, sec)]) for sec in security])

    fig, ax = plt.subplots(figsize=(11, 7))
    im = ax.imshow(matrix, cmap='Blues', aspect='auto')
    ax.set_title('Figure 01: Experiment Matrix Coverage')
    ax.set_xlabel('Security mode')
    ax.set_ylabel('Method / Scale')
    ax.set_xticks(range(len(security)), security)
    ax.set_yticks(range(len(labels)), labels)
    for i, row in enumerate(matrix):
        for j, v in enumerate(row):
            ax.text(j, i, str(v), ha='center', va='center', color='black', fontsize=8)
    fig.colorbar(im, ax=ax, label='Repetitions')
    plt.savefig(out)
    plt.close(fig)
