# Security Policy

## Scope

**IndustrialSemanticInterop** is a research and benchmarking framework. It includes benchmark modes that model authentication, encryption, failures, and security-related overhead, but it is **not a production security control, gateway, policy engine, or standards-certification product**.

## Reporting a vulnerability

Please do **not** disclose security-sensitive vulnerabilities in a public issue.

If GitHub's **Report a vulnerability** / private security advisory feature is enabled for this repository, use that channel so the report can be handled privately. Include:

- affected commit or version;
- affected component or file;
- reproduction steps or a minimal proof of concept;
- expected versus observed behavior;
- potential impact;
- any suggested mitigation, if known.

If a private GitHub security-reporting channel is unavailable, contact the repository owner through the GitHub profile rather than publishing exploit details.

## Research scenarios vs. real vulnerabilities

Fault injections and security modes under `configs/`, `scenarios/`, and benchmark code are intentional experimental constructs. A benchmarked authentication failure, endpoint outage, encryption overhead, or injected fault is not automatically a vulnerability in the framework itself.

## Responsible use

Do not treat benchmark results as evidence of production security certification. Any deployment using concepts from this repository should undergo independent threat modeling, implementation review, standards validation, and security testing appropriate to its operational environment.
