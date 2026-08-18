from analysis.plot_latency import plot_latency_distribution


def test_latency_boxplot_works_with_supported_matplotlib(tmp_path):
    rows = [
        {"method": "adaptive_selection", "latency_mean_ms": "1.2"},
        {"method": "direct_translation", "latency_mean_ms": "0.8"},
    ]
    output = tmp_path / "latency_distribution.png"

    plot_latency_distribution(rows, str(output))

    assert output.exists()
    assert output.stat().st_size > 10_000
