# Reproducibility Guide

- Python: 3.11+
- Deterministic seed control via `--seed` / `--base-seed`.
- Scenario configs are versioned in `scenarios/*.json`.
- Outputs include run-level JSON artifacts and aggregated summaries.

## Reproduce baseline run
```bash
python -m scripts.run_framework --repetitions 20 --seed 4242
```

## Separate exploratory vs final runs
- Exploratory: `--repetitions 3`
- Final descriptive benchmark: `--repetitions 20`
