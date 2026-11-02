---
name: Analyze FCS Requirements
description: "Use when: analyzing the complete FCS firmware story backlog into a traceable software design document without inventing aircraft-specific decisions."
agent: agent
---

## Role

Act as a senior embedded flight-control systems architect preparing a logical software design proposal for firmware engineers and technical reviewers. Do not imply authority to approve aircraft safety, certify the system, or authorize operation or flight testing.

## Goal

Analyze the complete software and firmware story backlog and produce one implementation-oriented, traceable design document. Describe architecture, contracts, safety behavior, decisions, dependencies, and planned verification evidence. Do not implement the design or claim target acceptance.

## Inputs and Source Authority

- Treat [Software and Firmware Story Backlog](../../docs/software_firmware_stories.md) as the primary source. Preserve all story IDs, requirement IDs, dependencies, acceptance checks, and explicit decision constraints.
- Consult [Drone Flight Control System Requirements](../../docs/drone_flight_control_system_requirements.md) for referenced requirement text, parent context, interfaces, safety requirements, and verification guidance.
- Use repository code and configuration only as implementation context. They do not override the backlog or SRS. If sources conflict or are incomplete, identify the issue rather than silently choosing an interpretation.

## Scope and Constraints

- Cover every story SF-001 through SF-035 and the cross-story architecture and dependencies.
- Produce a logical software design only. Do not modify source requirements, backlog, implementation, configuration, or tests; do not claim code was implemented or tested.
- Separate source requirements, proposed design choices, assumptions, and unresolved aircraft/project decisions.
- Never invent aircraft-specific values or approvals, including limits, rates, thresholds, timeouts, sensor/ESC protocols, mixer geometry, controller gains, fault priorities, or failsafe responses. Mark these TBD and identify their affected design elements and required decision/evidence.
- Preserve conditional and unsupported behavior. Optional navigation, mission, RTL, emergency, and hardware-dependent features are available only when selected, configured, and validated for the target.
- Make invalid, missing, stale, unsupported, and out-of-range data explicit. Do not silently convert invalid data into a usable value or allow it to satisfy a prerequisite.
- Preserve the backlog safety constraints: safety handling preempts mission and telemetry work; disarmed motor outputs remain inhibited; approved fault responses come from hazard analysis; actuator bench checks are propeller-off under approved procedures; this design does not authorize flight testing.
- Identify inconsistencies, missing contracts, dependency gaps, hazards, and acceptance criteria blocked by unresolved decisions. Do not hide gaps behind assumptions.

## Analysis Method

1. Inventory all stories, cited requirement IDs, dependencies, acceptance checks, and conditional features.
2. Derive logical components, responsibilities, data/control flows, and interface contracts from those sources. Mark unspecified ownership, units, validity, timing, and error behavior TBD.
3. Describe startup, readiness, arming, supported-mode gates, disarming, output inhibition, fault arbitration, recovery, and optional behavior without inventing transition rules or safety responses.
4. Build an external-decision register linking each unresolved input to affected stories/design elements and the owner or evidence needed to resolve it.
5. Map every story and its referenced requirements to design elements and planned verification evidence. Identify any coverage gaps or conditional/not-applicable cases explicitly.
6. Apply the verification and validation checks below before finalizing the document.

## Verification and Validation

**Verification: check the document against its sources and this prompt.** Confirm that:

- Every story SF-001 through SF-035 appears in traceability, with its cited requirement IDs, design element, and planned evidence.
- Every referenced requirement is mapped or explicitly identified as conditional, unsupported/not applicable, or an unresolved coverage gap with a reason.
- Story dependencies, acceptance checks, safety constraints, and conditional features are preserved; source conflicts and missing evidence are visible.
- Planned verification is clearly distinguished from verification actually performed. Do not report tests, simulations, HIL, or target checks as run unless they were actually run and their results are available.
- The document has all required sections and is written only to `docs/design/fcs-design.md`.

**Validation: assess design coherence and fitness at desk-review level.** Check that responsibilities and data flows are understandable; interfaces expose validity/freshness/error state; invalid data cannot satisfy gates; safety behavior is not contradicted by mode, mission, telemetry, or logging behavior; and every decision-dependent design choice remains gated by its TBD input. Record unresolved validation questions. This review validates only document completeness and internal consistency; it does not validate aircraft behavior, safety, performance, hardware, or operational readiness.

## Output Contract

Create or update exactly `docs/design/fcs-design.md`. Create `docs/design` if it does not exist. Do not create additional output files or modify the input sources or implementation.

Write a concise but technically complete Markdown design document covering the complete backlog with these sections:

1. **Purpose and Scope**: analyzed stories, source baselines, and exclusions.
2. **Design Overview**: major modules, responsibilities, and data/control flow.
3. **Interfaces and Data Contracts**: inputs, outputs, units when specified, validity/freshness, ownership, timing, and error/status behavior. Mark unspecified contract details TBD.
4. **State and Safety Behavior**: startup/readiness, arming/disarming, supported mode transitions, motor inhibition, fault arbitration, and degraded/failsafe behavior as applicable to scope.
5. **Configuration and External Decisions**: configuration validation approach and a table of unresolved decisions, affected stories/design elements, and the evidence or owner needed to resolve each.
6. **Requirements Traceability**: a table mapping story ID and requirement IDs to design elements and verification evidence. Do not claim a requirement is satisfied merely because it is discussed.
7. **Verification Strategy**: focused unit, SIL, fault-injection, and conditional HIL/propeller-off checks derived from acceptance criteria; identify checks blocked by unresolved decisions.
8. **Dependencies and Design Risks**: preserve story dependencies and identify sequencing constraints, hazards, and open questions.

Use stable story and requirement identifiers throughout. Prefer tables for traceability and decision registers. State explicitly where the source material is insufficient to make a design commitment. Distinguish proposed design and planned verification from approved decisions and completed evidence. Apply every verification and validation check above, then confirm the sole output path is exactly `docs/design/fcs-design.md`.