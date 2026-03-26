import csv
import itertools
from collections import defaultdict
from statistics import mean, stdev
import math


def compute_effect_sizes(rows, out_path: str = "results/aggregated/effect_sizes.csv"):
    grouped = defaultdict(list)
    for r in rows:
        grouped[(r["scale"], r["method"])].append(r["latency_mean_ms"])

    scales = sorted({k[0] for k in grouped})
    methods = sorted({k[1] for k in grouped})
    out = []
    for scale in scales:
        for m1, m2 in itertools.combinations(methods, 2):
            a = grouped.get((scale, m1), [])
            b = grouped.get((scale, m2), [])
            if not a or not b:
                continue
            mean_diff = mean(a) - mean(b)
            pooled = 0.0
            if len(a) > 1 and len(b) > 1:
                var_a = stdev(a) ** 2
                var_b = stdev(b) ** 2
                pooled = math.sqrt((((len(a) - 1) * var_a) + ((len(b) - 1) * var_b)) / max((len(a) + len(b) - 2), 1))
            out.append(
                {
                    "scale": scale,
                    "method_a": m1,
                    "method_b": m2,
                    "mean_diff_ms": mean_diff,
                    "cohens_d": (mean_diff / pooled) if pooled else 0.0,
                }
            )

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["scale", "method_a", "method_b", "mean_diff_ms", "cohens_d"])
        w.writeheader()
        w.writerows(out)
    return out
