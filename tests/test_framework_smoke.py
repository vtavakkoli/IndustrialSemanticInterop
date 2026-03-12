from pathlib import Path

from framework_benchmark.config import load_config
from framework_benchmark.runner import run_campaign, write_records


def test_core_smoke(tmp_path):
    cfg = load_config("configs/minimal.yaml")
    cfg["results"]["raw_dir"] = str(tmp_path / "raw")
    records = run_campaign(cfg)
    write_records(records, cfg["results"]["raw_dir"])
    assert records
    assert any(Path(cfg["results"]["raw_dir"]).glob("*.json"))
