# Reproducibility

Use deterministic config files (`configs/*.yaml`) and fixed seeds.

Run modes:
- Docker: `docker compose up --build`
- Native: `python -m framework_benchmark run --config configs/default.yaml`

Captured metadata includes git commit, platform, python version, timestamp, and run-level seeds.
