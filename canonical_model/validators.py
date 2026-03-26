"""Validation helpers for canonical interoperability messages."""

from __future__ import annotations

from typing import Any

from canonical_model.models import CanonicalMessage


def validate_canonical_message(message: CanonicalMessage) -> None:
    if not message.signal_id:
        raise ValueError("signal_id must be non-empty")
    if not isinstance(message.value, (int, float)):
        raise ValueError("value must be numeric")
    if not message.unit:
        raise ValueError("unit must be non-empty")
    if not message.timestamp:
        raise ValueError("timestamp must be present")


def compare_payload(actual: dict[str, Any], expected: dict[str, Any]) -> bool:
    """Return True when all expected key-value pairs are present in actual payload."""
    for key, value in expected.items():
        if isinstance(value, dict):
            node = actual.get(key)
            if not isinstance(node, dict) or not compare_payload(node, value):
                return False
            continue
        if actual.get(key) != value:
            return False
    return True
