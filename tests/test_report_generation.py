from pathlib import Path
from scripts.run_all import run_all


def test_report_generation(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    # minimal project structure for template import
    (tmp_path / "templates").mkdir()
    (tmp_path / "templates" / "report_template.md").write_text("{{ findings }}")
    run_all(repetitions=1)
    assert (tmp_path / "results" / "final_report.md").exists()
