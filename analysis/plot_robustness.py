from pathlib import Path
import json
from collections import defaultdict
from statistics import mean
from ._simple_plot import write_svg_bar


def plot_robustness(path="results/robustness", out="results/figures/robustness.svg"):
    files = list(Path(path).glob("*.json"))
    if not files:
        return
    rows = [json.loads(f.read_text()) for f in files]
    g = defaultdict(list)
    for r in rows:
        g[r['notes'].replace('fault=', '')].append(r['failure_rate'])
    labels = sorted(g)
    vals = [mean(g[k]) for k in labels]
    write_svg_bar(out, "Failure rate under faults", labels, vals)
