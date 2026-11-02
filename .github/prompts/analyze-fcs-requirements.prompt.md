---
name: Analyze FCS Requirements
description: Analyze the complete firmware story backlog and produce a traceable flight-control system design document without inventing aircraft-specific decisions.
agent: agent
---

Analyze the software and firmware story backlog and produce an implementation-oriented design document.

## Inputs

- Treat [Software and Firmware Story Backlog](../../docs/software_firmware_stories.md) as the primary source and preserve its story IDs, requirement IDs, dependencies, acceptance checks, and explicit decision constraints.
- Consult [Drone Flight Control System Requirements](../../docs/drone_flight_control_system_requirements.md) for the full text and context of referenced requirements.
- Analyze every story in the backlog and its cross-story architecture.
- Treat repository code and configuration as implementation context only. Do not silently use them to override the source requirements or backlog.

## Analysis Rules

- Separate stated requirements, design choices, assumptions, and unresolved aircraft/project decisions. Label each clearly.
- Never invent aircraft-specific values or approvals, including limits, rates, thresholds, timeouts, sensor/ESC protocols, mixer geometry, controller gains, fault priorities, or failsafe responses. Keep unresolved inputs as TBD and explain which design decisions depend on them.
- Preserve conditional and unsupported feature behavior. Do not present optional navigation, mission, RTL, emergency, or hardware-dependent behavior as universally available.
- Make invalid, missing, stale, and out-of-range data explicit in interfaces and behavior; do not propose silent fallback to a usable control value.
- Respect the backlog's safety constraints: safety handling preempts mission and telemetry work; motor inhibition while disarmed is explicit; approved fault responses come from hazard analysis; motor-output bench checks are propeller-off; this work does not authorize flight testing.
- Identify inconsistencies, missing interface contracts, dependency gaps, and acceptance criteria that cannot be made concrete until decisions are resolved. Do not conceal them with assumptions.
- Keep the design proportional to the backlog while covering every story and its cross-story dependencies.

## Output

Create or update exactly this artifact: `docs/design/fcs-design.md`. Create `docs/design` if it does not exist. Keep all generated design-document content under `docs/design`; do not modify the source backlog, requirements, implementation, or tests.

Write a concise but technically complete Markdown design document covering the complete backlog with these sections:

1. **Purpose and Scope**: analyzed stories, source baselines, and exclusions.
2. **Design Overview**: major modules, responsibilities, and data/control flow.
3. **Interfaces and Data Contracts**: inputs, outputs, units when specified, validity/freshness, ownership, timing, and error/status behavior. Mark unspecified contract details TBD.
4. **State and Safety Behavior**: startup/readiness, arming/disarming, supported mode transitions, motor inhibition, fault arbitration, and degraded/failsafe behavior as applicable to scope.
5. **Configuration and External Decisions**: configuration validation approach and a table of unresolved decisions, affected stories/design elements, and the evidence or owner needed to resolve each.
6. **Requirements Traceability**: a table mapping story ID and requirement IDs to design elements and verification evidence. Do not claim a requirement is satisfied merely because it is discussed.
7. **Verification Strategy**: focused unit, SIL, fault-injection, and conditional HIL/propeller-off checks derived from acceptance criteria; identify checks blocked by unresolved decisions.
8. **Dependencies and Design Risks**: preserve story dependencies and identify sequencing constraints, hazards, and open questions.

Use stable story and requirement identifiers throughout. Prefer tables for traceability and decision registers. State explicitly where the source material is insufficient to make a design commitment. Before finishing, check that every in-scope story and referenced requirement is either mapped, marked conditional/out of scope with a reason, or listed as an unresolved gap, and confirm the output path is exactly `docs/design/fcs-design.md`.