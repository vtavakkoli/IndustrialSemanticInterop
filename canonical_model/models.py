"""Canonical intermediate models for interoperability benchmarking."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(slots=True)
class CanonicalMessage:
    """Serializable canonical message used across protocol adapters."""

    signal_id: str
    value: float
    unit: str
    timestamp: str
    quality: str = "good"
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def now(cls, signal_id: str, value: float, unit: str, metadata: dict[str, Any] | None = None) -> "CanonicalMessage":
        return cls(
            signal_id=signal_id,
            value=value,
            unit=unit,
            timestamp=datetime.now(timezone.utc).isoformat(),
            metadata=metadata or {},
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
