"""Deterministic semantic transforms used by mapping engine."""

from __future__ import annotations


def celsius_to_kelvin(value: float) -> float:
    return value + 273.15


def identity(value: float) -> float:
    return value
