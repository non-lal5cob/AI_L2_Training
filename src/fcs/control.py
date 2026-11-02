"""Bounded setpoints and a configurable, disarmed-safe motor mixer."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Mapping

from .config import Bounds, MixerConfig
from .safety import ArmingState


@dataclass(frozen=True)
class ControlResult:
    values: tuple[float, ...]
    limited: bool


@dataclass(frozen=True)
class Command:
    timestamp: float
    values: Mapping[str, float]


@dataclass(frozen=True)
class CommandResult:
    accepted: bool
    reason: str | None = None
    setpoints: tuple[float, ...] = ()


def validate_command(
    command: Command | None,
    now: float,
    max_age_s: float,
    bounds: Mapping[str, Bounds],
) -> CommandResult:
    if command is None:
        return CommandResult(False, "missing")
    if (
        isinstance(now, bool)
        or not isinstance(now, (int, float))
        or not isfinite(now)
        or isinstance(command.timestamp, bool)
        or not isinstance(command.timestamp, (int, float))
        or not isfinite(command.timestamp)
    ):
        return CommandResult(False, "invalid_timestamp")
    if (
        isinstance(max_age_s, bool)
        or not isinstance(max_age_s, (int, float))
        or not isfinite(max_age_s)
        or max_age_s <= 0
    ):
        raise ValueError("max_age_s must be a positive finite number")
    if command.timestamp > now:
        return CommandResult(False, "future_timestamp")
    if now - command.timestamp > max_age_s:
        return CommandResult(False, "stale")
    if set(command.values) != set(bounds):
        return CommandResult(False, "command_fields_mismatch")
    values: list[float] = []
    for name, bound in bounds.items():
        value = command.values[name]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
            return CommandResult(False, f"invalid:{name}")
        if not bound.contains(value):
            return CommandResult(False, f"out_of_range:{name}")
        values.append(float(value))
    return CommandResult(True, setpoints=tuple(values))


def limit_setpoints(
    setpoints: Mapping[str, float], bounds: Mapping[str, Bounds]
) -> ControlResult:
    if set(setpoints) != set(bounds):
        raise ValueError("setpoint names must exactly match configured bounds")
    values: list[float] = []
    limited = False
    for name, bound in bounds.items():
        value = setpoints[name]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
            raise ValueError(f"setpoint {name} must be finite")
        bounded = min(bound.maximum, max(bound.minimum, value))
        limited |= bounded != value
        values.append(bounded)
    return ControlResult(tuple(values), limited)


def motor_outputs(
    setpoints: tuple[float, ...], mixer: MixerConfig, state: ArmingState
) -> ControlResult:
    if state is ArmingState.DISARMED:
        return ControlResult((mixer.inhibited_value,) * len(mixer.matrix), False)
    if len(setpoints) != len(mixer.matrix[0]):
        raise ValueError("setpoint count does not match mixer inputs")
    outputs: list[float] = []
    limited = False
    for row in mixer.matrix:
        raw = 0.0
        for coefficient, setpoint in zip(row, setpoints):
            if isinstance(setpoint, bool) or not isinstance(setpoint, (int, float)) or not isfinite(setpoint):
                raise ValueError("motor mixer inputs must be finite")
            raw += coefficient * setpoint
        output = min(mixer.output_bounds.maximum, max(mixer.output_bounds.minimum, raw))
        limited |= output != raw
        outputs.append(output)
    return ControlResult(tuple(outputs), limited)