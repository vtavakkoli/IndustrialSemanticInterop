"""Representative IEEE 1451-style source adapter (bounded scope)."""

from __future__ import annotations

from typing import Any

from adapters.base import ProtocolAdapter
from canonical_model.models import CanonicalMessage
from canonical_model.validators import compare_payload, validate_canonical_message


class IEEE1451StyleAdapter(ProtocolAdapter):
    name = "ieee1451_style"

    def __init__(self) -> None:
        self._processed = 0

    def load_source(self, source_payload: dict[str, Any]) -> dict[str, Any]:
        return dict(source_payload)

    def normalize_message(self, raw_payload: dict[str, Any]) -> dict[str, Any]:
        teds = raw_payload.get("teds", {})
        return {
            "signal_id": raw_payload["transducer_channel"],
            "value": float(raw_payload["measurement"]),
            "unit": teds.get("unit", raw_payload.get("unit", "unknown")),
            "timestamp": raw_payload["timestamp"],
            "metadata": {
                "manufacturer": teds.get("manufacturer", "unknown"),
                "model": teds.get("model_number", "unknown"),
                "serial": teds.get("serial_number", "n/a"),
            },
        }

    def map_to_canonical_model(self, normalized_payload: dict[str, Any]) -> CanonicalMessage:
        message = CanonicalMessage(**normalized_payload)
        validate_canonical_message(message)
        return message

    def translate_to_target(self, canonical_message: CanonicalMessage) -> dict[str, Any]:
        return canonical_message.to_dict()

    def send_to_target(self, translated_payload: dict[str, Any]) -> dict[str, Any]:
        self._processed += 1
        return translated_payload

    def validate_roundtrip(self, sent_payload: dict[str, Any], expected_payload: dict[str, Any]) -> bool:
        return compare_payload(sent_payload, expected_payload)

    def collect_metrics(self) -> dict[str, float]:
        return {"messages_processed": float(self._processed)}
