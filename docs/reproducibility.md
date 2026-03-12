# Reproducibility Guide

- Python: 3.11+
- Deterministic seed control via `--seed` / `--base-seed`.
- Scenario configs are versioned in `scenarios/*.json`.
- Outputs include run-level JSON artifacts and aggregated summaries.

## Reproduce baseline run (local)
```bash
python -m scripts.run_framework --repetitions 20 --seed 4242
```

## Reproduce baseline run (Docker)
```bash
docker compose up --build
```

## Separate exploratory vs final runs
- Exploratory: `--repetitions 3`
- Final descriptive benchmark: `--repetitions 20`

## Stdout progress
The framework reports step-by-step progress to stdout for long runs, including scenario start/completion and overall run percentage.
