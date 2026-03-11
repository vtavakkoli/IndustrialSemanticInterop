from scripts.run_all import run_all


def test_run_all_creates_structure(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "templates").mkdir()
    (tmp_path / "templates" / "report_template.md").write_text("ok")
    run_all(repetitions=1)
    for sub in ["raw_runs", "aggregated", "ablations", "robustness", "figures", "environment"]:
        assert (tmp_path / "results" / sub).exists()
