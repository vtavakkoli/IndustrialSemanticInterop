"""Representative OPC UA bridge adapter using node-write exchange payloads."""

from __future__ import annotations

from typing import Any

from adapters.base import ProtocolAdapter
from canonical_model.models import CanonicalMessage
from canonical_model.validators import compare_payload


class OPCUABridgeAdapter(ProtocolAdapter):
    name = "opcua_bridge"

    def __init__(self, namespace: int = 2) -> None:
        self.namespace = namespace
        self._processed = 0

    def load_source(self, source_payload: dict[str, Any]) -> dict[str, Any]:
        return source_payload

    def normalize_message(self, raw_payload: dict[str, Any]) -> dict[str, Any]:
        return raw_payload

    def map_to_canonical_model(self, normalized_payload: dict[str, Any]) -> CanonicalMessage:
        return CanonicalMessage(**normalized_payload)

    def translate_to_target(self, canonical_message: CanonicalMessage) -> dict[str, Any]:
        return {
            "node_id": f"ns={self.namespace};s={canonical_message.signal_id}",
            "value": canonical_message.value,
            "unit": canonical_message.unit,
            "source_timestamp": canonical_message.timestamp,
            "status_code": canonical_message.quality,
            "attributes": canonical_message.metadata,
        }

    def send_to_target(self, translated_payload: dict[str, Any]) -> dict[str, Any]:
        self._processed += 1
        return translated_payload

    def validate_roundtrip(self, sent_payload: dict[str, Any], expected_payload: dict[str, Any]) -> bool:
        return compare_payload(sent_payload, expected_payload)

    def collect_metrics(self) -> dict[str, float]:
        return {"messages_processed": float(self._processed)}
