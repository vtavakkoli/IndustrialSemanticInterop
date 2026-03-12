"""Base abstraction for protocol adapters."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from canonical_model.models import CanonicalMessage


class ProtocolAdapter(ABC):
    """Formal adapter interface used by benchmark pipelines."""

    name: str

    @abstractmethod
    def load_source(self, source_payload: dict[str, Any]) -> dict[str, Any]:
        """Load a raw source payload into an adapter-internal structure."""

    @abstractmethod
    def normalize_message(self, raw_payload: dict[str, Any]) -> dict[str, Any]:
        """Normalize protocol-specific fields for deterministic processing."""

    @abstractmethod
    def map_to_canonical_model(self, normalized_payload: dict[str, Any]) -> CanonicalMessage:
        """Map normalized payload into canonical intermediate model."""

    @abstractmethod
    def translate_to_target(self, canonical_message: CanonicalMessage) -> dict[str, Any]:
        """Translate canonical message into target protocol representation."""

    @abstractmethod
    def send_to_target(self, translated_payload: dict[str, Any]) -> dict[str, Any]:
        """Perform transport step (mock transport in current prototype)."""

    @abstractmethod
    def validate_roundtrip(self, sent_payload: dict[str, Any], expected_payload: dict[str, Any]) -> bool:
        """Validate target payload against scenario expectation."""

    @abstractmethod
    def collect_metrics(self) -> dict[str, float]:
        """Expose adapter-local counters useful for benchmark diagnostics."""
