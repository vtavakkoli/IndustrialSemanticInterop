from scripts.run_all import run_all


def test_run_all_creates_structure(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    run_all(repetitions=1)
    for sub in ["raw_runs", "aggregated", "ablations", "robustness", "figures", "environment"]:
        assert (tmp_path / "results" / sub).exists()
    figs = list((tmp_path / "results" / "figures").glob("figure_*.png"))
    assert len(figs) == 18
