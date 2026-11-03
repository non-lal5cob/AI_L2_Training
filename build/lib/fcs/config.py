"""Validated configuration types; all aircraft values are supplied by callers."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Mapping


def _finite(value: float, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
        raise ValueError(f"{name} must be a finite number")


@dataclass(frozen=True)
class Bounds:
    minimum: float
    maximum: float

    def __post_init__(self) -> None:
        _finite(self.minimum, "minimum")
        _finite(self.maximum, "maximum")
        if self.minimum >= self.maximum:
            raise ValueError("minimum must be less than maximum")

    def contains(self, value: float) -> bool:
        return self.minimum <= value <= self.maximum


@dataclass(frozen=True)
class SensorRule:
    fields: Mapping[str, Bounds]
    max_age_s: float

    def __post_init__(self) -> None:
        _finite(self.max_age_s, "max_age_s")
        if self.max_age_s <= 0:
            raise ValueError("max_age_s must be greater than zero")
        if not isinstance(self.fields, Mapping) or not self.fields:
            raise ValueError("sensor fields must be explicitly configured")
        if any(not isinstance(name, str) or not name for name in self.fields):
            raise ValueError("sensor field names must be non-empty strings")
        if any(not isinstance(bounds, Bounds) for bounds in self.fields.values()):
            raise ValueError("each sensor field requires validated bounds")


@dataclass(frozen=True)
class MixerConfig:
    matrix: tuple[tuple[float, ...], ...]
    output_bounds: Bounds
    inhibited_value: float

    def __post_init__(self) -> None:
        _finite(self.inhibited_value, "inhibited_value")
        if not isinstance(self.matrix, tuple) or not self.matrix or not self.matrix[0]:
            raise ValueError("mixer matrix must not be empty")
        input_count = len(self.matrix[0])
        if any(not isinstance(row, tuple) for row in self.matrix):
            raise ValueError("mixer matrix rows must be immutable tuples")
        if any(len(row) != input_count for row in self.matrix):
            raise ValueError("mixer matrix rows must have equal length")
        for row in self.matrix:
            for value in row:
                _finite(value, "mixer coefficient")
        if not self.output_bounds.contains(self.inhibited_value):
            raise ValueError("inhibited_value must be within output bounds")


@dataclass(frozen=True)
class FcsConfig:
    sensor_rules: Mapping[str, SensorRule]
    command_bounds: Mapping[str, Bounds]
    mixer: MixerConfig

    def __post_init__(self) -> None:
        if not isinstance(self.sensor_rules, Mapping) or not self.sensor_rules:
            raise ValueError("at least one sensor rule must be configured")
        if not isinstance(self.command_bounds, Mapping) or not self.command_bounds:
            raise ValueError("at least one command bound must be configured")
        if any(not isinstance(name, str) or not name for name in self.sensor_rules):
            raise ValueError("sensor names must be non-empty strings")
        if any(not isinstance(rule, SensorRule) for rule in self.sensor_rules.values()):
            raise ValueError("each sensor requires a validated rule")
        if any(not isinstance(name, str) or not name for name in self.command_bounds):
            raise ValueError("command names must be non-empty strings")
        if any(not isinstance(bound, Bounds) for bound in self.command_bounds.values()):
            raise ValueError("each command requires validated bounds")
        if not isinstance(self.mixer, MixerConfig):
            raise ValueError("a validated mixer configuration is required")
        if len(self.mixer.matrix[0]) != len(self.command_bounds):
            raise ValueError("mixer input count must match configured commands")