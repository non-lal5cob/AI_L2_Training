"""Deterministic, hardware-independent flight-control software core."""

from .config import Bounds, FcsConfig, MixerConfig, SensorRule
from .control import Command, CommandResult, ControlResult, limit_setpoints, motor_outputs, validate_command
from .safety import ArmingGate, ArmingState, FaultPolicy, StartupCheck
from .sensors import SampleResult, SensorSample, validate_sample

__all__ = [
    "ArmingGate",
    "ArmingState",
    "Bounds",
    "Command",
    "CommandResult",
    "ControlResult",
    "FaultPolicy",
    "FcsConfig",
    "MixerConfig",
    "SampleResult",
    "SensorRule",
    "SensorSample",
    "StartupCheck",
    "limit_setpoints",
    "motor_outputs",
    "validate_command",
    "validate_sample",
]