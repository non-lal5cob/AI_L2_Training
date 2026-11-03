"""Sensor sample validation with explicit invalidity reasons."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Mapping

from .config import SensorRule


@dataclass(frozen=True)
class SensorSample:
    timestamp: float
    values: Mapping[str, float]


@dataclass(frozen=True)
class SampleResult:
    valid: bool
    reason: str | None = None


def validate_sample(
    sample: SensorSample | None,
    rule: SensorRule,
    now: float,
    previous_timestamp: float | None = None,
) -> SampleResult:
    if sample is None:
        return SampleResult(False, "missing")
    if (
        isinstance(sample.timestamp, bool)
        or not isinstance(sample.timestamp, (int, float))
        or not isfinite(sample.timestamp)
        or isinstance(now, bool)
        or not isinstance(now, (int, float))
        or not isfinite(now)
    ):
        return SampleResult(False, "invalid_timestamp")
    if sample.timestamp > now:
        return SampleResult(False, "future_timestamp")
    if now - sample.timestamp > rule.max_age_s:
        return SampleResult(False, "stale")
    if previous_timestamp is not None and sample.timestamp <= previous_timestamp:
        return SampleResult(False, "out_of_order")
    for field, bounds in rule.fields.items():
        value = sample.values.get(field)
        if value is None:
            return SampleResult(False, f"missing:{field}")
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
            return SampleResult(False, f"invalid:{field}")
        if not bounds.contains(value):
            return SampleResult(False, f"out_of_range:{field}")
    return SampleResult(True)