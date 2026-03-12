import subprocess


def test_framework_run_emits_progress_logs():
    proc = subprocess.run(
        ["python", "-m", "framework_benchmark", "run", "--config", "configs/minimal.yaml"],
        check=True,
        capture_output=True,
        text=True,
    )
    out = proc.stdout
    assert "[framework_benchmark] running campaign" in out
    assert "[framework_benchmark] progress:" in out
    assert "[framework_benchmark] run command completed" in out
