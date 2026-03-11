from scripts.run_all import run_all


def test_report_generation(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    run_all(repetitions=1)
    html = (tmp_path / "results" / "final_report.html").read_text()
    assert "<h1>Industrial Semantic Interoperability Benchmark Report</h1>" in html
    assert "<pre>" not in html
    assert "figure_01_experiment_matrix.png" in html
