---
name: fcs-unit-test-spec
description: 'Create or review a traceable FCS unit-test specification in CSV from the logical design, software/firmware stories, and requirements. Use for FCS test design, test-oracle gaps, automation readiness, or CSV validation; never implement or execute tests.'
argument-hint: '[design, story, and requirement inputs or requested story IDs]'
---

# FCS Unit-Test Specification

Create or review a reviewable, implementation-oriented unit-test specification for the FCS. The sole project artifact produced or revised by this workflow is `docs/fcs-unit-test-spec.csv`. The skill's bundled schema, reference, and validator are supporting resources and are not generated outputs.

## Use This Skill When

- Deriving unit-level cases from the FCS logical design, story backlog, or SRS.
- Reviewing traceability, test-oracle completeness, or automation readiness of the specification.
- Narrowing proposed tests to deterministic public behavior that can be isolated from external dependencies.

Do not use it to implement software, modify source requirements/backlog/design, create executable unit tests, run tests, or claim verification. Test cases must use Python standard-library concepts and local fakes/stubs or dependency injection; do not require hardware, networks, external services/data, or third-party test/helper libraries.

## Authority and Safety Boundaries

1. Treat `docs/design/fcs-design.md` as the primary design input. Cross-check each behavior against `docs/software_firmware_stories.md` and the referenced material in `docs/drone_flight_control_system_requirements.md`.
2. Requirements and backlog control when sources differ. Preserve IDs, dependencies, acceptance checks, safety constraints, and conditional behavior. Record conflicts and gaps instead of resolving them silently.
3. Use implementation, configuration, and tests only as context; they do not override normative sources.
4. Never invent aircraft-specific values, limits, thresholds, timing budgets, protocols, calibration procedures, fault priorities, failsafe responses, or acceptance criteria. Use symbolic inputs and identify required decisions/evidence as TBD.
5. Keep hardware, SIL, HIL, propeller-off bench, and target evidence outside unit cases. When behavior cannot be isolated, record a gap or out-of-scope item rather than labeling integration behavior a unit test.
6. Preserve distinctions among valid, invalid, missing, stale, unsupported, and out-of-range data wherever required. Invalid data must not satisfy prerequisites or silently become usable. Preserve disarmed motor-output inhibition and safety priority; do not prescribe unapproved fault behavior.
7. Do not imply safety approval, certification, operational readiness, or authorization for operation or flight testing.

## Procedure

1. Read the design, story backlog, and SRS; identify the requested scope and the source IDs that apply. Use source code/configuration/tests only to identify possible unit boundaries or seams.
2. Extract behaviors that a single unit can expose deterministically. Identify collaborator seams, preconditions, injected inputs, expected observable results, dependencies, applicability, and external decisions.
3. For each case, define one public behavior and a precise oracle. Include positive, negative, boundary, missing/stale/invalid, or interaction inputs only when supported by the sources. Prefer local fakes, stubs, explicit configuration, and deterministic time.
4. Classify each case `PROPOSED`, `BLOCKED`, `CONDITIONAL`, or `NOT_APPLICABLE`. Give every blocked or conditional case the decision/evidence that would resolve it. Do not treat proposed specification as executed verification.
5. Add `GAP` records for underspecified unit oracles and uncovered acceptance criteria. Add `OUT_OF_SCOPE` records for SIL, integration, HIL, bench, target, or other non-unit evidence with its reason and dependency.
6. Check traceability: every story SF-001 through SF-035 and every requirement cited by a case has a corresponding `CASE`, `GAP`, or `OUT_OF_SCOPE` record. Distinguish specification coverage from demonstrated verification.
7. Write only `docs/fcs-unit-test-spec.csv` for the specification itself. Use the fixed contract in [CSV contract](./references/csv-contract.md) and [schema](./assets/spec-schema.json). Do not create additional project output files.
8. Run the bundled standard-library validator after creating or revising the CSV:

   ```powershell
   python .github/skills/fcs-unit-test-spec/scripts/validate_spec.py
   ```

   The validator checks structural/traceability invariants, not behavioral correctness or safety. Resolve structural failures; report remaining source-level decisions as gaps, not as passing test evidence. Do not run pytest or claim tests were executed.

## Completion Criteria

- The CSV has exactly the required header, valid one-record-per-line CSV, recognized record types, and unique stable record IDs.
- Every `CASE` has its required traceability, setup, input, observable result, and status fields; decision-dependent cases identify their blocker/evidence.
- Every story SF-001 through SF-035 appears in a `CASE`, `GAP`, or `OUT_OF_SCOPE` record, and all referenced requirement IDs exist in the SRS.
- The context record explicitly states this is specification/traceability review only and does not demonstrate software behavior, safety, performance, compatibility, or operational readiness.
- The validator result and any unresolved or unverified decisions are reported accurately.

See [review notes](./references/review-notes.md) for status decisions and validation limits.