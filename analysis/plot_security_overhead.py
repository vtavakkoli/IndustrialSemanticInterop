from collections import defaultdict

from .mpl_config import setup_matplotlib

setup_matplotlib()

import matplotlib.pyplot as plt


def plot_security_latency(rows, out='results/figures/figure_08_security_latency_overhead.png'):
    sec = ['none', 'auth', 'encryption', 'full']
    vals = defaultdict(list)
    for r in rows:
        vals[r['security']].append(float(r['latency_mean_ms']))
    ys = [sum(vals[s]) / max(1, len(vals[s])) for s in sec]

    fig, ax = plt.subplots(figsize=(11, 7))
    ax.bar(sec, ys, color=['#66c2a5', '#fc8d62', '#8da0cb', '#e78ac3'])
    ax.set_title('Figure 08: Security Latency Overhead')
    ax.set_xlabel('Security mode')
    ax.set_ylabel('Latency (ms)')
    ax.grid(axis='y', alpha=0.3)
    plt.savefig(out)
    plt.close(fig)


def plot_security_throughput(rows, out='results/figures/figure_09_security_throughput_overhead.png'):
    sec = ['none', 'auth', 'encryption', 'full']
    vals = defaultdict(list)
    for r in rows:
        vals[r['security']].append(float(r['throughput_msg_per_sec']))
    ys = [sum(vals[s]) / max(1, len(vals[s])) for s in sec]

    fig, ax = plt.subplots(figsize=(11, 7))
    ax.bar(sec, ys, color=['#66c2a5', '#fc8d62', '#8da0cb', '#e78ac3'])
    ax.set_title('Figure 09: Security Throughput Overhead')
    ax.set_xlabel('Security mode')
    ax.set_ylabel('Throughput (msg/s)')
    ax.grid(axis='y', alpha=0.3)
    plt.savefig(out)
    plt.close(fig)
