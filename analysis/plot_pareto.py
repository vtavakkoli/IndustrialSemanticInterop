from ._simple_plot import write_svg_scatter


def plot_pareto(rows, out="results/figures/pareto_latency_throughput.svg"):
    pts = [(r['latency_mean_ms'], r['throughput_msg_per_sec'], r['method']) for r in rows[:60]]
    write_svg_scatter(out, "Latency/Throughput Pareto view", pts)
