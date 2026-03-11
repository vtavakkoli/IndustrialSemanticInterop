import csv
import itertools
from collections import defaultdict
from statistics import mean


def compute_effect_sizes(rows, out_path: str = "results/aggregated/effect_sizes.csv"):
    grouped = defaultdict(list)
    for r in rows:
        grouped[(r["scale"], r["method"])].append(r["latency_mean_ms"])

    scales = sorted({k[0] for k in grouped})
    methods = sorted({k[1] for k in grouped})
    out = []
    for scale in scales:
        for m1, m2 in itertools.combinations(methods, 2):
            a = grouped[(scale, m1)]
            b = grouped[(scale, m2)]
            out.append({"scale": scale, "method_a": m1, "method_b": m2, "mean_diff_ms": mean(a) - mean(b)})

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["scale", "method_a", "method_b", "mean_diff_ms"])
        w.writeheader(); w.writerows(out)
    return out
