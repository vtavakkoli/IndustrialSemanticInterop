from pathlib import Path
from benchmarks.benchmark_runner import run_benchmarks


def test_benchmark_outputs_written(tmp_path):
    out = tmp_path / "raw"
    run_benchmarks(repetitions=1, output=str(out))
    assert len(list(Path(out).glob("*.json"))) > 0
