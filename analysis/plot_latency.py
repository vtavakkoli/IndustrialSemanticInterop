from ._simple_plot import write_svg_bar


def plot_latency(rows, out="results/figures/latency_distribution.svg"):
    labels = [f"{r['method']}|{r['security']}" for r in rows[:30]]
    vals = [r["latency_mean_ms"] for r in rows[:30]]
    write_svg_bar(out, "Latency distribution (sampled runs)", labels, vals, "ms")
