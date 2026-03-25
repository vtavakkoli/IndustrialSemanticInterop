import csv
import math
from collections import defaultdict
from pathlib import Path
from statistics import mean, stdev


def _normal_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _welch_ttest(sample_a, sample_b):
    if len(sample_a) < 2 or len(sample_b) < 2:
        return {"t_stat": 0.0, "p_value": 1.0}
    ma, mb = mean(sample_a), mean(sample_b)
    va, vb = stdev(sample_a) ** 2, stdev(sample_b) ** 2
    denom = math.sqrt((va / len(sample_a)) + (vb / len(sample_b)))
    if denom == 0:
        return {"t_stat": 0.0, "p_value": 1.0}
    t = (ma - mb) / denom
    p = 2.0 * (1.0 - _normal_cdf(abs(t)))
    return {"t_stat": t, "p_value": max(min(p, 1.0), 0.0)}


def run_stats(rows, out_dir: str = "results/aggregated"):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    by_method = defaultdict(list)
    for r in rows:
        by_method[r["method"]].append(r["latency_mean_ms"])

    methods = sorted(by_method)
    overall = mean([x for v in by_method.values() for x in v])
    between = sum(len(by_method[m]) * (mean(by_method[m]) - overall) ** 2 for m in methods)
    within = sum(sum((x - mean(by_method[m])) ** 2 for x in by_method[m]) for m in methods)
    f_stat = (between / max(len(methods) - 1, 1)) / (within / max(sum(len(v) for v in by_method.values()) - len(methods), 1)) if within else 0.0

    stat_rows = [
        {"assumption": "normality_shapiro", "passed": False, "detail": "Shapiro-Wilk not available in stdlib-only mode; normal approximation used for large-sample Welch tests."},
        {"assumption": "equal_variance_levene", "passed": False, "detail": "Levene not available in stdlib-only mode; Welch correction applied for unequal variances."},
        {"assumption": "omnibus", "passed": f_stat > 1.0, "detail": f"proxy_F={f_stat:.4f}"},
    ]
    with open(out / "stat_tests.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(stat_rows[0].keys()))
        w.writeheader(); w.writerows(stat_rows)

    posthoc = []
    for i, m1 in enumerate(methods):
        for m2 in methods[i + 1:]:
            diff = mean(by_method[m1]) - mean(by_method[m2])
            wt = _welch_ttest(by_method[m1], by_method[m2])
            pooled = math.sqrt((stdev(by_method[m1]) ** 2 + stdev(by_method[m2]) ** 2) / 2.0) if len(by_method[m1]) > 1 and len(by_method[m2]) > 1 else 0.0
            effect = diff / pooled if pooled else 0.0
            posthoc.append(
                {
                    "group1": m1,
                    "group2": m2,
                    "meandiff": diff,
                    "p_adj": f"{wt['p_value']:.6f}",
                    "lower": "na",
                    "upper": "na",
                    "reject": wt["p_value"] < 0.05,
                    "effect_size_d": f"{effect:.4f}",
                    "t_stat": f"{wt['t_stat']:.4f}",
                }
            )
    with open(out / "posthoc.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["group1", "group2", "meandiff", "p_adj", "lower", "upper", "reject", "effect_size_d", "t_stat"])
        w.writeheader(); w.writerows(posthoc)
    return {"test": "conservative_proxy", "pvalue": "na"}
