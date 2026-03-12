"""Rule-based mapping engine for canonical message normalization."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from canonical_model.models import CanonicalMessage
from mappings.transforms import celsius_to_kelvin, identity

TRANSFORMS = {
    "celsius_to_kelvin": celsius_to_kelvin,
    "identity": identity,
}


class MappingEngine:
    def __init__(self, rules: dict[str, Any] | None = None) -> None:
        self.rules = rules or {}

    def apply(self, message: CanonicalMessage) -> CanonicalMessage:
        updated = deepcopy(message)
        unit_rule = self.rules.get("unit_conversion")
        if unit_rule:
            transform = TRANSFORMS[unit_rule["transform"]]
            updated.value = transform(updated.value)
            updated.unit = unit_rule["target_unit"]

        metadata_fields = self.rules.get("metadata_projection", [])
        if metadata_fields:
            updated.metadata = {k: updated.metadata.get(k) for k in metadata_fields}
        return updated
