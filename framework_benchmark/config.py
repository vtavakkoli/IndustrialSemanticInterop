from __future__ import annotations

import ast
from pathlib import Path
from typing import Any


DEFAULT_CONFIG: dict[str, Any] = {
    "repetitions": 3,
    "seed": 4242,
    "strategies": ["ontology_based", "direct_translation", "soa", "opcua_mediated", "adaptive_selection"],
    "policies": ["balanced", "latency_first", "semantics_first", "fault_resilient", "security_first"],
    "scales": ["small", "medium", "large"],
    "security_modes": ["none", "auth", "encryption", "full"],
    "scenario_flags": ["none", "high_load", "secure_and_semantic", "multi_constraint_mixed"],
    "results": {"raw_dir": "results/raw_runs", "aggregated_dir": "results/aggregated", "report_html": "results/final_report.html"},
}


def deep_update(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    out = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = deep_update(out[key], value)
        else:
            out[key] = value
    return out


def _parse_scalar(raw: str) -> Any:
    text = raw.strip()
    if text in {"true", "True"}:
        return True
    if text in {"false", "False"}:
        return False
    if text.startswith("[") and text.endswith("]"):
        try:
            return ast.literal_eval(text)
        except Exception:
            inner = text[1:-1].strip()
            if not inner:
                return []
            return [_parse_scalar(token.strip()) for token in inner.split(",")]
    if text.isdigit() or (text.startswith("-") and text[1:].isdigit()):
        return int(text)
    try:
        return float(text)
    except ValueError:
        return text.strip('"').strip("'")


def _parse_yaml_minimal(content: str) -> dict[str, Any]:
    data: dict[str, Any] = {}
    current_key: str | None = None
    for line in content.splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        if line.startswith("  - ") and current_key:
            if not isinstance(data.get(current_key), list):
                data[current_key] = []
            data[current_key].append(_parse_scalar(line[4:]))
            continue
        if line.startswith("  ") and current_key and ":" in line:
            sub_key, raw = line.strip().split(":", 1)
            data.setdefault(current_key, {})[sub_key.strip()] = _parse_scalar(raw)
            continue
        if ":" in line:
            key, raw = line.split(":", 1)
            key = key.strip()
            raw = raw.strip()
            current_key = key
            if raw == "":
                data[key] = {}
            else:
                data[key] = _parse_scalar(raw)
    return data


def load_config(path: str | None = None) -> dict[str, Any]:
    if not path:
        return dict(DEFAULT_CONFIG)
    cfg_path = Path(path)
    if not cfg_path.exists():
        raise FileNotFoundError(f"Config not found: {path}")
    user_cfg = _parse_yaml_minimal(cfg_path.read_text(encoding="utf-8"))
    return deep_update(DEFAULT_CONFIG, user_cfg)
