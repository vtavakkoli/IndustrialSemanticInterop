from ._simple_plot import write_svg_bar


def plot_throughput(rows, out="results/figures/throughput_vs_load.svg"):
    labels = [f"{r['method']}|{r['scale']}" for r in rows[:30]]
    vals = [r["throughput_msg_per_sec"] for r in rows[:30]]
    write_svg_bar(out, "Throughput vs load (sampled runs)", labels, vals)
