"""Hybrid pipeline adapter chaining OPC UA bridge with IEC 61499 exchange conversion."""

from __future__ import annotations

from typing import Any

from adapters.base import ProtocolAdapter
from adapters.iec61499_adapter import IEC61499StyleAdapter
from adapters.opcua_adapter import OPCUABridgeAdapter
from canonical_model.models import CanonicalMessage


class HybridPipelineAdapter(ProtocolAdapter):
    name = "hybrid_pipeline"

    def __init__(self) -> None:
        self.opcua = OPCUABridgeAdapter()
        self.iec = IEC61499StyleAdapter()

    def load_source(self, source_payload: dict[str, Any]) -> dict[str, Any]:
        return source_payload

    def normalize_message(self, raw_payload: dict[str, Any]) -> dict[str, Any]:
        return raw_payload

    def map_to_canonical_model(self, normalized_payload: dict[str, Any]) -> CanonicalMessage:
        return CanonicalMessage(**normalized_payload)

    def translate_to_target(self, canonical_message: CanonicalMessage) -> dict[str, Any]:
        opcua_payload = self.opcua.translate_to_target(canonical_message)
        # representative bridge step: expose OPC UA node in metadata before IEC 61499 exchange
        canonical_message.metadata["opcua_node_id"] = opcua_payload["node_id"]
        return self.iec.translate_to_target(canonical_message)

    def send_to_target(self, translated_payload: dict[str, Any]) -> dict[str, Any]:
        return self.iec.send_to_target(translated_payload)

    def validate_roundtrip(self, sent_payload: dict[str, Any], expected_payload: dict[str, Any]) -> bool:
        return self.iec.validate_roundtrip(sent_payload, expected_payload)

    def collect_metrics(self) -> dict[str, float]:
        metrics = self.opcua.collect_metrics()
        metrics.update({f"iec_{k}": v for k, v in self.iec.collect_metrics().items()})
        return metrics
