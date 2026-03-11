"""
Script to generate final result figures and enhanced figures based on collected
performance metrics.  It reads the provided ``performance_metrics.json`` and
``performance_summary.csv`` files located in the results directory and
produces a set of charts summarising latency, throughput, resource usage,
scalability, security overhead and integration time for the different
integration approaches.  A radar chart provides a holistic view across
multiple metrics.  The figures are saved into the ``figures`` and
``enhanced_figures`` subdirectories inside the specified output directory.

Usage:

    python generate_final_results.py --output_dir path/to/results

If run without arguments the script defaults to ``results`` in the project
root.
"""
from __future__ import annotations

import argparse
import json
import os
from typing import Dict, List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


def _ensure_dirs(base_dir: str) -> tuple[str, str]:
    """Ensure the figures and enhanced_figures directories exist.

    Args:
        base_dir: Root directory under which ``figures`` and ``enhanced_figures``
            subdirectories should be created.

    Returns:
        A tuple of paths to (figures_dir, enhanced_dir).
    """
    figures_dir = os.path.join(base_dir, "figures")
    enhanced_dir = os.path.join(base_dir, "enhanced_figures")
    os.makedirs(figures_dir, exist_ok=True)
    os.makedirs(enhanced_dir, exist_ok=True)
    return figures_dir, enhanced_dir


def _load_metrics(output_dir: str) -> tuple[Dict[str, dict], pd.DataFrame]:
    """Load performance metrics and summary information.

    Args:
        output_dir: Directory containing ``performance_metrics.json`` and
            ``performance_summary.csv``.

    Returns:
        A tuple of (performance_metrics, performance_summary_df).
    """
    metrics_path = os.path.join(output_dir, "performance_metrics.json")
    summary_path = os.path.join(output_dir, "performance_summary.csv")
    if not os.path.exists(metrics_path) or not os.path.exists(summary_path):
        raise FileNotFoundError(
            f"Expected performance_metrics.json and performance_summary.csv in {output_dir}."
        )
    with open(metrics_path, "r") as f:
        metrics = json.load(f)
    summary_df = pd.read_csv(summary_path)
    return metrics, summary_df


def _plot_integration_time(metrics: Dict[str, dict], methods: List[str], figures_dir: str) -> None:
    """Plot integration time comparison across methods.

    Args:
        metrics: Parsed performance metrics.
        methods: List of integration methods to include.
        figures_dir: Directory to save the figure.
    """
    # --- START OF CORRECTION ---

    # 1. Get the original data in hours
    total_times_hours = [metrics["integration_time"][m]["total_time"] for m in methods]

    # 2. Convert from hours to milliseconds for plotting
    # (1 hour * 3600 sec/hour * 1000 ms/sec)
    times_ms = [t * 3600 * 1000 for t in total_times_hours]

    # 3. Create the plot using the new millisecond values
    plt.figure(figsize=(8, 5))
    sns.barplot(x=methods, y=times_ms, palette="viridis")

    # 4. Update titles and labels to reflect the new unit (ms)
    # Using "Startup Configuration Time" to match the paper's text for Figure 8.
    plt.title("Startup Configuration Time Comparison")
    plt.xlabel("Integration Approach")
    plt.ylabel("Startup Configuration Time (ms)")

    # 5. Annotate the bars with the correct millisecond values
    # The offset for the text is also adjusted to work with the new scale of values.
    for idx, val in enumerate(times_ms):
        plt.text(idx, val + max(times_ms) * 0.02, f"{val:.2f}", ha="center")

    # --- END OF CORRECTION ---

    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, "integration_time_comparison.png"))
    plt.close()


def _plot_latency(metrics: Dict[str, dict], methods: List[str], figures_dir: str) -> None:
    """Plot latency comparison using medium scale average latencies.

    Args:
        metrics: Parsed performance metrics.
        methods: List of integration methods to include.
        figures_dir: Directory to save the figure.
    """
    latencies = [metrics["latency"][m]["medium_scale"]["avg"] for m in methods]
    plt.figure(figsize=(8, 5))
    sns.barplot(x=methods, y=latencies, palette="magma")
    plt.title("Latency Comparison (Medium Scale)")
    plt.xlabel("Integration Approach")
    plt.ylabel("Average Latency (ms)")
    for idx, val in enumerate(latencies):
        plt.text(idx, val + max(latencies) * 0.02, f"{val:.2f}", ha="center")
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, "latency_comparison.png"))
    plt.close()


def _plot_throughput(metrics: Dict[str, dict], methods: List[str], figures_dir: str) -> None:
    """Plot throughput comparison using medium scale throughputs.

    Args:
        metrics: Parsed performance metrics.
        methods: List of integration methods to include.
        figures_dir: Directory to save the figure.
    """
    throughputs = [metrics["throughput"][m]["medium_scale"] for m in methods]
    plt.figure(figsize=(8, 5))
    sns.barplot(x=methods, y=throughputs, palette="cubehelix")
    plt.title("Throughput Comparison (Medium Scale)")
    plt.xlabel("Integration Approach")
    plt.ylabel("Throughput (msg/s)")
    for idx, val in enumerate(throughputs):
        plt.text(idx, val + max(throughputs) * 0.02, f"{val:.0f}", ha="center")
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, "throughput_comparison.png"))
    plt.close()


def _plot_resource_usage(metrics: Dict[str, dict], summary: pd.DataFrame, methods: List[str], figures_dir: str) -> None:
    """Plot CPU and memory usage comparison using a secondary y-axis.

    Args:
        metrics: Parsed performance metrics.
        summary: Summary DataFrame containing memory usage.
        methods: List of integration methods to include.
        figures_dir: Directory to save the figure.
    """
    cpu_values = [metrics["cpu_usage"][m]["medium_scale"] for m in methods]
    mem_values = []
    for m in methods:
        row = summary[summary["Method"] == m]
        mem_values.append(float(row["Memory Usage (MB)"].iloc[0]))

    # --- START OF CORRECTION ---

    # 1. Setup the plot and the primary y-axis (for CPU)
    fig, ax1 = plt.subplots(figsize=(10, 6))
    
    # 2. Create the secondary y-axis (for Memory), sharing the x-axis
    ax2 = ax1.twinx()

    # 3. Set up bar positions and width for side-by-side bars
    x = np.arange(len(methods))  # the label locations [0, 1, 2, 3, 4]
    width = 0.4  # the width of the bars

    # Use colors that match the paper's figure
    cpu_color = '#66c2a5'
    mem_color = '#fc8d62'

    # 4. Plot the bars
    # Plot CPU bars on the left axis (ax1)
    rects1 = ax1.bar(x - width/2, cpu_values, width, label='CPU Usage (%)', color=cpu_color)
    # Plot Memory bars on the right axis (ax2)
    rects2 = ax2.bar(x + width/2, mem_values, width, label='Memory Usage (MB)', color=mem_color)

    # 5. Set labels, titles, and ticks
    ax1.set_xlabel('Integration Approach')
    ax1.set_ylabel('CPU Usage (%)', color=cpu_color)
    ax2.set_ylabel('Memory Usage (MB)', color=mem_color)
    ax1.tick_params(axis='y', labelcolor=cpu_color)
    ax2.tick_params(axis='y', labelcolor=mem_color)
    
    # Set the x-axis tick labels to be the method names
    ax1.set_xticks(x)
    ax1.set_xticklabels(methods)
    
    plt.title('Resource Usage Comparison (Medium Scale)')

    # 6. Add a combined legend
    # Get handles and labels from both axes and combine them
    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    plt.legend(h1 + h2, l1 + l2, title='Resource', loc='upper left')

    # 7. Use the robust bar_label function for annotations
    ax1.bar_label(rects1, padding=3, fmt='%.1f')
    ax2.bar_label(rects2, padding=3, fmt='%.1f')
    
    # Set y-axis limits to give some space at the top
    ax1.set_ylim(0, max(cpu_values) * 1.5)
    ax2.set_ylim(0, max(mem_values) * 1.1)

    # --- END OF CORRECTION ---

    fig.tight_layout()  # Use fig.tight_layout() when working with Axes objects
    plt.savefig(os.path.join(figures_dir, "resource_usage_comparison.png"))
    plt.close()


def _plot_scalability(metrics: Dict[str, dict], methods: List[str], figures_dir: str) -> None:
    """Plot scalability comparison showing latency and throughput across different scales.

    Args:
        metrics: Parsed performance metrics.
        methods: List of integration methods to include.
        figures_dir: Directory to save the figure.
    """
    scales = [10, 50, 100, 500, 1000, 5000]
    plt.figure(figsize=(10, 6))
    for m in methods:
        latencies = [metrics["scalability"][m][str(s)]["latency"] for s in scales]
        plt.plot(scales, latencies, marker="o", label=f"{m} Latency")
    plt.title("Scalability Analysis - Latency vs. Number of Devices")
    plt.xlabel("Number of Devices")
    plt.ylabel("Latency (ms)")
    plt.xscale("log")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, "scalability_comparison.png"))
    plt.close()

    # Throughput
    plt.figure(figsize=(10, 6))
    for m in methods:
        throughputs = [metrics["scalability"][m][str(s)]["throughput"] for s in scales]
        plt.plot(scales, throughputs, marker="o", label=f"{m} Throughput")
    plt.title("Scalability Analysis - Throughput vs. Number of Devices")
    plt.xlabel("Number of Devices")
    plt.ylabel("Throughput (msg/s)")
    plt.xscale("log")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, "scalability_throughput_comparison.png"))
    plt.close()


def _plot_security_overhead(metrics: Dict[str, dict], methods: List[str], figures_dir: str) -> None:
    """Plot security overhead comparison using full security mode.

    Args:
        metrics: Parsed performance metrics.
        methods: List of integration methods to include.
        figures_dir: Directory to save the figure.
    """
    lat_overheads = [metrics["security_overhead"][m]["full"]["latency_overhead"] for m in methods]
    thr_reductions = [metrics["security_overhead"][m]["full"]["throughput_reduction"] for m in methods]
    
    df = pd.DataFrame({
        "Method": methods * 2,
        "Metric": ["Latency Overhead (%)"] * len(methods) + ["Throughput Reduction (%)"] * len(methods),
        "Value": lat_overheads + thr_reductions
    })
    
    plt.figure(figsize=(10, 6)) # Increased size for better readability
    
    # Use specific colors to closely match the paper's figure
    palette = {"Latency Overhead (%)": "#FBB4AE", "Throughput Reduction (%)": "#B3CDE3"}
    
    # --- START OF CORRECTION ---

    # 1. Create the plot and get the Axes object
    ax = sns.barplot(x="Method", y="Value", hue="Metric", data=df, palette=palette)

    # 2. Use a robust method to annotate bars
    # This iterates through the actual bar objects ('patches') on the plot
    for p in ax.patches:
        ax.annotate(f'{p.get_height():.3f}', 
                    (p.get_x() + p.get_width() / 2., p.get_height()), 
                    ha = 'center', va = 'center', 
                    xytext = (0, 9), 
                    textcoords = 'offset points')

    # --- END OF CORRECTION ---
    
    plt.title("Security Overhead Comparison (Full Security)")
    plt.xlabel("Integration Approach")
    plt.ylabel("Overhead (%)")
    
    # Improve legend placement
    plt.legend(title='Metric', loc='upper left')

    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, "security_overhead_comparison.png"))
    plt.close()


def _plot_max_throughput(metrics: Dict[str, dict], methods: List[str], figures_dir: str) -> None:
    """Plot maximum throughput comparison across methods.

    The maximum throughput represents the theoretical upper bound on message
    processing rate for each integration approach.  It is derived from the
    inverse of the processing interval used in the wrapper service.

    Args:
        metrics: Parsed performance metrics containing ``max_throughput``.
        methods: List of integration methods to include.
        figures_dir: Directory to save the figure.
    """
    # Guard against missing data
    if "max_throughput" not in metrics:
        return
    max_tps = [metrics["max_throughput"][m] for m in methods]
    plt.figure(figsize=(8, 5))
    sns.barplot(x=methods, y=max_tps, palette="Blues_d")
    plt.title("Maximum Throughput Comparison")
    plt.xlabel("Integration Approach")
    plt.ylabel("Max Throughput (msg/s)")
    for idx, val in enumerate(max_tps):
        plt.text(idx, val + max(max_tps) * 0.02, f"{val:.0f}", ha="center")
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, "max_throughput_comparison.png"))
    plt.close()


def _plot_radar(metrics: Dict[str, dict], methods: List[str], figures_dir: str) -> None:
    """Generate a radar chart to provide an overall comparison across multiple metrics.

    The radar chart normalises metrics so that larger values always indicate better
    performance.  Latency, CPU usage, integration time and security overhead are
    inverted since smaller values are preferable.

    Args:
        metrics: Parsed performance metrics.
        methods: List of integration methods to include.
        figures_dir: Directory to save the figure.
    """
    # Define metrics to include: label -> (extractor, is_better_when_higher)
    metric_defs = {
        "Latency": (lambda m: metrics["latency"][m]["medium_scale"]["avg"], False),
        "Throughput": (lambda m: metrics["throughput"][m]["medium_scale"], True),
        "CPU Usage": (lambda m: metrics["cpu_usage"][m]["medium_scale"], False),
        "Scalability": (
            lambda m: 1 / metrics["scalability"][m]["1000"]["latency"], True
        ),
        "Security Overhead": (
            lambda m: metrics["security_overhead"][m]["full"]["latency_overhead"], False
        ),
        "Integration Time": (
            lambda m: metrics["integration_time"][m]["total_time"], False
        ),
    }
    # Extract raw values
    raw = {label: [func(m) for m in methods] for label, (func, _) in metric_defs.items()}
    # Normalise values: for each metric scale to 0..1
    norm = {}
    for label, values in raw.items():
        if label == "CPU Idle" :
            max_val = min(values)
            min_val = max(values)
        else:
            max_val = max(values)
            min_val = min(values)
        # If metric is better when higher, normalise directly; otherwise invert
        is_higher_better = metric_defs[label][1]
        scaled = []
        for val in values:
            if max_val == min_val:
                norm_val = 1.0
            else:
                norm_val = (val - min_val) / (max_val - min_val)
            scaled.append(norm_val if is_higher_better else 1 - norm_val)
        norm[label] = scaled
    # Prepare angles for radar
    labels = list(metric_defs.keys())
    num_vars = len(labels)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]
    plt.figure(figsize=(8, 8))
    ax = plt.subplot(111, polar=True)
    for idx, m in enumerate(methods):
        values = [norm[label][idx] for label in labels]
        values += values[:1]
        ax.plot(angles, values, label=m)
        ax.fill(angles, values, alpha=0.1)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    ax.set_yticklabels([])
    ax.set_title("Integration Approach Comparison Radar Chart")
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1))
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, "radar_chart_comparison.png"))
    plt.close()


def generate_results(output_dir: str = "results") -> None:
    """Generate all final result figures and tables.

    Args:
        output_dir: Directory containing performance data and where to place
            generated figures.  Defaults to ``results``.
    """
    figures_dir, enhanced_dir = _ensure_dirs(os.path.join(output_dir))
    metrics, summary_df = _load_metrics(output_dir)
    methods = list(metrics["latency"].keys())

    # Basic figures
    _plot_integration_time(metrics, methods, figures_dir)
    _plot_latency(metrics, methods, figures_dir)
    _plot_throughput(metrics, methods, figures_dir)
    _plot_resource_usage(metrics, summary_df, methods, figures_dir)
    _plot_scalability(metrics, methods, figures_dir)
    _plot_security_overhead(metrics, methods, figures_dir)
    _plot_radar(metrics, methods, figures_dir)
    _plot_max_throughput(metrics, methods, figures_dir)

    # Generate summary table as a figure in the enhanced directory
    summary_table_path = os.path.join(enhanced_dir, "comprehensive_comparison_table.png")
    _create_summary_table(metrics, summary_df, methods, summary_table_path)

    # Additional enhanced figures
    _create_security_impact_analysis(metrics, methods, os.path.join(enhanced_dir, "security_impact_analysis.png"))
    _create_scalability_analysis(metrics, methods, os.path.join(enhanced_dir, "scalability_analysis.png"))
    _create_method_recommendation(metrics, summary_df, methods, os.path.join(enhanced_dir, "method_recommendation.png"))


def _create_summary_table(metrics: Dict[str, dict], summary: pd.DataFrame, methods: List[str], output_path: str) -> None:
    """Create a comprehensive comparison table as an image.

    The table includes key metrics for each integration method.

    Args:
        metrics: Parsed performance metrics.
        summary: Summary DataFrame containing memory usage and message size.
        methods: List of methods to include.
        output_path: File path to save the table image.
    """
    # Build data for table
    rows = []
    for m in methods:
        row = {
            "Method": m,
            "Latency (ms)": f"{metrics['latency'][m]['medium_scale']['avg']:.2f}",
            "Throughput (msg/s)": f"{metrics['throughput'][m]['medium_scale']:.0f}",
            "Max Throughput (msg/s)": f"{metrics['max_throughput'].get(m, 0):.0f}",
            "CPU Usage (%)": f"{metrics['cpu_usage'][m]['medium_scale']:.1f}",
            "Memory Usage (MB)": f"{float(summary[summary['Method'] == m]['Memory Usage (MB)'].iloc[0]):.1f}",
            "Integration Time (ms)": f"{metrics['integration_time_ms'][m]:.2f}",
            "Security Overhead (%)": f"{metrics['security_overhead'][m]['full']['latency_overhead']:.1f}",
            "Message Size (KB)": f"{float(summary[summary['Method'] == m]['Message Size (KB)'].iloc[0]):.2f}"
        }
        rows.append(row)
    df = pd.DataFrame(rows)
    fig, ax = plt.subplots(figsize=(10, 2 + 0.3 * len(methods)))
    ax.axis("off")
    table = ax.table(
        cellText=df.values,
        colLabels=df.columns,
        loc="center",
        cellLoc="center",
        colLoc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1, 1.5)
    plt.title("Comprehensive Comparison Table")
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()


def _create_security_impact_analysis(metrics: Dict[str, dict], methods: List[str], output_path: str) -> None:
    """Create a bar chart focusing on security overhead impacts for latency and throughput.

    Args:
        metrics: Parsed performance metrics.
        methods: Integration methods.
        output_path: Path to save the figure.
    """
    lat_full = [metrics['security_overhead'][m]['full']['latency_overhead'] for m in methods]
    thr_full = [metrics['security_overhead'][m]['full']['throughput_reduction'] for m in methods]
    lat_enc = [metrics['security_overhead'][m]['encryption']['latency_overhead'] for m in methods]
    thr_enc = [metrics['security_overhead'][m]['encryption']['throughput_reduction'] for m in methods]
    lat_auth = [metrics['security_overhead'][m]['authentication']['latency_overhead'] for m in methods]
    thr_auth = [metrics['security_overhead'][m]['authentication']['throughput_reduction'] for m in methods]

    df = pd.DataFrame({
        'Method': methods * 3 * 2,
        'Security Mode': (['Full'] * len(methods) + ['Encryption'] * len(methods) + ['Authentication'] * len(methods)) * 2,
        'Metric': ['Latency Overhead (%)'] * len(methods) * 3 + ['Throughput Reduction (%)'] * len(methods) * 3,
        'Value': lat_full + lat_enc + lat_auth + thr_full + thr_enc + thr_auth
    })
    plt.figure(figsize=(12, 6))
    sns.barplot(x="Method", y="Value", hue="Security Mode", data=df[df['Metric'] == 'Latency Overhead (%)'], palette="Blues")
    plt.title("Security Impact Analysis - Latency Overhead by Mode")
    plt.ylabel("Overhead (%)")
    plt.xlabel("Integration Approach")
    plt.tight_layout()
    plt.savefig(output_path.replace(".png", "_latency.png"))
    plt.close()
    plt.figure(figsize=(12, 6))
    sns.barplot(x="Method", y="Value", hue="Security Mode", data=df[df['Metric'] == 'Throughput Reduction (%)'], palette="Greens")
    plt.title("Security Impact Analysis - Throughput Reduction by Mode")
    plt.ylabel("Reduction (%)")
    plt.xlabel("Integration Approach")
    plt.tight_layout()
    plt.savefig(output_path.replace(".png", "_throughput.png"))
    plt.close()


def _create_scalability_analysis(metrics: Dict[str, dict], methods: List[str], output_path: str) -> None:
    """Create a line chart focusing on scalability for a selection of scales.

    Args:
        metrics: Parsed performance metrics.
        methods: Integration methods.
        output_path: Path to save the figure.
    """
    scales = [10, 100, 1000, 5000]
    plt.figure(figsize=(10, 6))
    for m in methods:
        latencies = [metrics['scalability'][m][str(s)]['latency'] for s in scales]
        plt.plot(scales, latencies, marker='o', label=m)
    plt.xscale('log')
    plt.title('Scalability Analysis - Latency across Scales')
    plt.xlabel('Number of Devices (log scale)')
    plt.ylabel('Latency (ms)')
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def _create_method_recommendation(metrics: Dict[str, dict], summary: pd.DataFrame, methods: List[str], output_path: str) -> None:
    """Generate a simple recommendation figure based on weighted scores.

    This function scores each method across multiple metrics and highlights the
    method with the highest overall score as the recommended integration
    approach.

    Args:
        metrics: Parsed performance metrics.
        summary: Summary DataFrame containing memory usage.
        methods: Integration methods.
        output_path: Path to save the figure.
    """
    # Weights for each metric (higher is better).  Adjust weights as desired.
    weights = {
        'Latency': -0.3,  # negative weight because lower latency is better
        'Throughput': 0.3,
        'CPU Usage': -0.1,  # lower CPU usage is better
        'Memory Usage': -0.1,  # lower memory is better
        'Integration Time': -0.1,  # lower integration time is better
        'Security Overhead': -0.1  # lower overhead is better
    }
    scores = {}
    for m in methods:
        score = 0.0
        # Latency (medium scale)
        score += weights['Latency'] * metrics['latency'][m]['medium_scale']['avg']
        # Throughput (medium scale)
        score += weights['Throughput'] * metrics['throughput'][m]['medium_scale']
        # CPU usage
        score += weights['CPU Usage'] * metrics['cpu_usage'][m]['medium_scale']
        # Memory usage
        mem_val = float(summary[summary['Method'] == m]['Memory Usage (MB)'].iloc[0])
        score += weights['Memory Usage'] * mem_val
        # Integration time
        score += weights['Integration Time'] * metrics['integration_time'][m]['total_time']
        # Security overhead (full)
        score += weights['Security Overhead'] * metrics['security_overhead'][m]['full']['latency_overhead']
        scores[m] = score
    # Determine recommendation
    recommended_method = max(scores, key=scores.get)
    # Create bar chart for scores
    plt.figure(figsize=(8, 5))
    sns.barplot(x=list(scores.keys()), y=list(scores.values()), palette="coolwarm")
    plt.title("Method Recommendation Based on Weighted Score")
    plt.xlabel("Integration Approach")
    plt.ylabel("Score (higher is better)")
    # Annotate recommendation
    for idx, (method, score) in enumerate(scores.items()):
        plt.text(idx, score + max(scores.values()) * 0.02, f"{score:.2f}", ha='center')
    plt.axhline(y=scores[recommended_method], color='grey', linestyle='--', alpha=0.5)
    plt.text(len(scores) - 0.5, scores[recommended_method] + max(scores.values()) * 0.05,
             f"Recommended: {recommended_method}", ha='right', fontsize=10, color='green')
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate final result figures from performance metrics.")
    parser.add_argument(
        "--output_dir",
        type=str,
        default="results",
        help="Directory containing performance_metrics.json and performance_summary.csv and where figures will be saved",
    )
    args = parser.parse_args()
    generate_results(args.output_dir)


if __name__ == "__main__":
    main()