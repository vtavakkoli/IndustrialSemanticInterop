from pathlib import Path
from benchmarks.ablation_runner import run_ablations


def test_ablation_outputs(tmp_path):
    out = tmp_path / "abl"
    run_ablations(repetitions=1, output=str(out))
    assert any(Path(out).glob("*.json"))
