from pathlib import Path
import json
from ._simple_plot import write_svg_bar


def plot_ablations(path="results/ablations", out="results/figures/ablations.svg"):
    files = list(Path(path).glob("*.json"))
    if not files:
        return
    rows = [json.loads(f.read_text()) for f in files[:40]]
    labels = [r['method'] for r in rows]
    vals = [r['throughput_msg_per_sec'] for r in rows]
    write_svg_bar(out, "Ablation throughput", labels, vals)
