# AGENTS.md

## Project Title:
Drone Flight Control System (FCS) — Training Baseline

## Project Description:
Small multirotor flight-control work aligned to the drone FCS requirements baseline. Focus on sensor validation, state estimation, stabilization, flight-mode logic, arming safety, and failsafe behavior with clear traceability and testable verification.

## Folder Structure:
- docs/ — requirements and design references
- src/ — sensor, navigation, control, and safety modules
- tests/ — unit, integration, and fault-injection checks
- simulation/ — SIL/HIL scenarios and validation runs
- config/ — aircraft limits, calibration, and mode parameters

## Tech Stack:
Python 3.11+, NumPy/SciPy, pytest, black, ruff; optional simulation/telemetry tools only when required. Keep logic deterministic and easy to validate.

## Testing Framework along with examples:
Use pytest for unit and integration checks. Examples: test_sensor_validation, test_arming_gate, test_failsafe_on_sensor_loss, test_mode_transition. Run the smallest relevant suite first and require passing regression tests before merge.

## Linting and Formatting:
black + ruff (or equivalent); keep type hints, docstrings, and function boundaries consistent; treat warnings as errors in CI.

## Simulation Standards:
Use SIL/HIL simulations for startup, arming, sensor invalidity, lost control input, battery thresholds, landing, and failsafe behavior. Model realistic signal delays, noise, and timeout scenarios. Never assume a safe result without verification.

## External library references:
docs/drone_flight_control_system_requirements.md; aircraft and sensor datasheets; approved simulation or protocol libraries; avoid unreviewed dependencies in safety-critical paths.

## Handling Sensitive Data:
Do not commit secrets, aircraft identifiers, telemetry, personal data, or production calibration. Redact logs before sharing and keep sensitive material outside the repository.

## Requirements and Safety Rules:
- Maintain traceability to requirement IDs and verification methods.
- Validate all inputs and reject missing, stale, or out-of-range data.
- Enforce mode, altitude, rate, and battery limits explicitly.
- Failsafe behavior must be driven by hazard analysis and safe-state design.
- No silent fallback from invalid sensor data or unsafe conditions.

