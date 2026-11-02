"""Readiness, arming, and configured fault arbitration."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping


@dataclass(frozen=True)
class StartupCheck:
    name: str
    passed: bool
    critical: bool = True


class ArmingState(str, Enum):
    DISARMED = "disarmed"
    ARMED = "armed"


class ArmingGate:
    def __init__(self) -> None:
        self.state = ArmingState.DISARMED
        self.inhibit_reasons: tuple[str, ...] = ("not_ready",)

    def request_arm(
        self,
        checks: tuple[StartupCheck, ...],
        config_valid: bool,
        sensors_valid: bool,
        active_faults: tuple[str, ...] = (),
    ) -> bool:
        reasons = [f"startup:{check.name}" for check in checks if check.critical and not check.passed]
        if not checks:
            reasons.append("startup_checks_missing")
        if not config_valid:
            reasons.append("configuration_invalid")
        if not sensors_valid:
            reasons.append("sensor_status_invalid")
        reasons.extend(f"fault:{fault}" for fault in active_faults)
        self.inhibit_reasons = tuple(reasons)
        if self.state is ArmingState.ARMED or reasons:
            return False
        self.state = ArmingState.ARMED
        return True

    def disarm(self) -> None:
        self.state = ArmingState.DISARMED
        self.inhibit_reasons = ("disarmed",)


@dataclass(frozen=True)
class FaultPolicy:
    priorities: Mapping[str, int]
    responses: Mapping[str, str]

    def __post_init__(self) -> None:
        if not self.priorities or set(self.priorities) != set(self.responses):
            raise ValueError("each configured fault must have exactly one priority and response")
        if any(isinstance(priority, bool) or not isinstance(priority, int) for priority in self.priorities.values()):
            raise ValueError("fault priorities must be integers")
        if any(not response for response in self.responses.values()):
            raise ValueError("fault responses must be explicit and non-empty")

    def select(self, active_faults: tuple[str, ...]) -> tuple[str, str] | None:
        if not active_faults:
            return None
        unknown = set(active_faults) - self.priorities.keys()
        if unknown:
            raise ValueError(f"faults lack approved policy: {', '.join(sorted(unknown))}")
        selected = min(active_faults, key=lambda fault: (-self.priorities[fault], fault))
        return selected, self.responses[selected]