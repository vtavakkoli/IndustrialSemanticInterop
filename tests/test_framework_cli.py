import subprocess


def test_framework_validate_cli_runs():
    proc = subprocess.run(
        ["python", "-m", "framework_benchmark", "validate", "--config", "configs/minimal.yaml"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "Configuration valid" in proc.stdout
