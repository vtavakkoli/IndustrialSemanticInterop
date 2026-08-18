# Contributing

Thank you for helping improve **IndustrialSemanticInterop**. Contributions are most useful when they preserve the benchmark's reproducibility, claim boundaries, and comparability across strategies.

## Contribution priorities

We welcome contributions that:

- add clearly scoped interoperability strategy baselines;
- improve benchmark reproducibility or deterministic execution;
- add tests for adapters, mappings, scenarios, metrics, or report generation;
- extend fault, scale, or security scenarios without changing existing semantics silently;
- improve documentation, result validation, or scientific reporting;
- fix defects without altering published benchmark behavior unintentionally.

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
```

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest -q
```

Docker users can reproduce the default benchmark with:

```bash
docker compose up --build
```

## Pull request expectations

A focused pull request should explain:

1. **What changed** and why.
2. **Which benchmark dimensions are affected** (strategy, policy, scale, security, fault scenario, metrics, or reporting).
3. **Whether published/default behavior changes**.
4. **How the change was validated**.
5. **Any limitations or new assumptions** introduced by the change.

Please keep unrelated refactors separate from scientific or behavioral changes.

## Scientific integrity

Changes that affect experimental behavior should preserve or explicitly document:

- deterministic seeds;
- configuration values;
- strategy labels and scenario semantics;
- raw outputs needed to reproduce aggregate results;
- environment information for publication-oriented runs;
- the distinction between representative standards-informed adapters and formal standards conformance.

Do not strengthen claims in documentation unless the repository contains corresponding evidence. The current claim boundaries are documented in [`docs/paper_claim_boundary.md`](docs/paper_claim_boundary.md).

## Tests

Before submitting a change, run:

```bash
pytest -q
```

For benchmark or analysis changes, also run the smallest relevant configuration first, then the full workflow if practical.

## Style

- Prefer small, readable Python functions with explicit inputs and outputs.
- Keep benchmark configuration in YAML/JSON rather than hard-coding experimental parameters.
- Add tests for new behavior.
- Avoid committing generated caches, virtual environments, or large transient outputs.
- Document any new metric or scenario sufficiently for another researcher to reproduce it.

## Reporting issues

For ordinary bugs or research questions, include the commit SHA, operating system, Python version, configuration file, command used, and a minimal reproducible example when possible.

For security-sensitive issues, follow [`SECURITY.md`](SECURITY.md) rather than opening a public vulnerability report.
