# Flight Control System Software Design

**Document ID:** FCS-SDD-001  
**Version:** 0.1  
**Status:** Derived design baseline; aircraft-specific decisions remain open  
**Date:** 2 November 2026

## 1. Purpose and Scope

This document turns the complete software and firmware backlog into a logical design and verification framework for the training-baseline multirotor flight control system. It covers stories SF-001 through SF-035 and their cited requirements. The primary source is [Software and Firmware Story Backlog](../software_firmware_stories.md); [DFC-SRS-001, v1.0](../drone_flight_control_system_requirements.md) supplies the parent requirement context.

This is a software architecture and interface design, not a target implementation, aircraft-specific safety assessment, certification claim, or authorization to operate or flight-test an aircraft. The SRS and backlog are generic baselines. Optional functions are available only when selected, configured, and validated for the target aircraft. Target acceptance is blocked wherever an external decision or approved safety input is still TBD.

### Design basis

- **Source requirements:** IDs and acceptance checks in DFC-SRS-001 and the backlog are treated as normative inputs to this design.
- **Design choices:** Responsibilities and logical interfaces below are proposed to preserve module independence, explicit validity, deterministic control flow, and safety priority.
- **Assumptions:** The baseline is a multirotor with independently controlled motors and at least an IMU, as stated by DFC-SRS-001. Actual airframe, sensor set, hardware, and enabled modes are not established.
- **Unresolved inputs:** Every aircraft-specific value, protocol, mode, response, and acceptance limit not stated by an approved project baseline remains TBD. No default value is implied.

## 2. Design Overview

### Logical components

| Component | Responsibility and boundary |
|---|---|
| Configuration and build identity | Load and validate versioned flight configuration before use; expose source revision, target, and configuration identity. Reject missing, malformed, unsupported, or out-of-range values. Runtime inputs cannot modify protected parameters while armed. Schema, ranges, storage protection, and toolchain are TBD. |
| Startup and readiness manager | Execute the approved deterministic startup sequence; initialize all configured sensor and actuator interfaces; collect supported processor, memory, sensor, and communication self-test results; coordinate only the declared calibration procedures; publish readiness or an observable inhibit reason. The check inventory, criticality, sequence, readiness criteria, and reporting interface details are TBD. If the selected reporting interface fails during startup, any alternate path or other observable reporting behavior is also TBD. |
| Platform and device adapters | Isolate processor/RTOS, clocks, IMU, optional sensors, ESCs, battery, pilot link, telemetry, and storage. Normalize data only using approved protocol, units, scaling, and sign conventions. Report interface errors rather than manufacturing valid-looking data. |
| Sensor validation and health | Check configured freshness, ordering, physical plausibility, and communication status. Publish samples with timestamp/alignment metadata and explicit validity plus reason. Limits and detection budgets are TBD. |
| State estimation | Consume validated sensor samples and produce attitude/rates and, when configured, altitude, position, velocity, and heading estimates. Each output carries validity/confidence and source-availability status. Algorithm, alignment, latency, and validity criteria are TBD. |
| Pilot command and mission input | Parse and validate command format, range, and freshness; map accepted pilot commands to mode-specific setpoints. Mission input is separately validated and cannot arm the aircraft. Protocols, ranges, timeouts, authentication/pairing, and invalid-command action are TBD. |
| Setpoint and control | Apply configured envelope and transition-rate bounds, attitude/rate control, and integral protection. Invalid state or setpoints cannot yield unrestricted demands. Gains, loop rates, limits, and performance criteria are TBD. |
| Mode manager | Own supported-mode availability and transitions. Gate entry and continued operation on required valid state, command, configuration, and arming status. Expose active mode and transition reason. Supported modes and transition priorities are TBD. |
| Allocation and actuator output | Allocate bounded control demands using validated, configured airframe geometry; report saturation; constrain outputs to the configured ESC range. Apply the configured inhibit output whenever disarmed. Geometry, channel order, direction, protocol, ranges, and inhibit value are TBD. |
| Safety supervisor and fault arbiter | Collect fault/status events, apply the aircraft-approved severity/response/recovery table, arbitrate concurrent faults deterministically, and veto lower-priority work. No response or priority is selected here without hazard-analysis approval. |
| Runtime monitor and scheduler | Measure execution deadlines, cycle frequency, and end-to-end latency; detect overload and watchdog/reset conditions; expose observable status and prevent reset/restart from spuriously arming. Platform, schedule, budgets, watchdog design, and reset response are TBD. |
| Health, telemetry, and event log | Publish supported health, mode, arming, sensor, battery, and safety status; reject malformed/unsupported messages; record ordered/timestamped events where storage permits. These functions are bounded so they cannot starve the control path. Protocol, event schema, rates, storage, and retention are TBD. |
| Optional navigation, envelope, and mission services | Provide configured source validity, enabled envelope checks, mission validation/execution, Altitude Hold, Position Hold, RTL, and takeoff/landing only when supported and approved. These services cannot bypass safety gates or use invalid/unavailable navigation. |

### Data and control flow

1. Startup loads and validates configuration and build identity, then follows the approved sequence to initialize every configured sensor and actuator interface, run supported self-tests, and perform calibration only under its declared procedure. Readiness or an inhibit reason is observable through the selected GCS or pilot interface. A configured critical-check failure prevents readiness and arming; the exact sequence, check criticality, and readiness criteria remain TBD.
2. Device adapters publish timestamped/aligned readings and communication status. Sensor validation marks each reading valid or invalid with a reason; consumers must not infer validity from a numeric value such as zero.
3. Estimation publishes required state and validity. The mode manager exposes only configured modes whose prerequisites are valid. Pilot commands are validated and converted to mode-specific setpoints; accepted missions remain inert until separately authorized by supported mode/state logic.
4. Setpoint limiting and control produce bounded demands. Allocation constrains motor commands and reports saturation. The safety supervisor can inhibit or select an approved response; while disarmed, the actuator boundary always applies the configured inhibit value.
5. Runtime monitoring, health reporting, telemetry, and logging observe this flow through bounded interfaces. Safety events take precedence over mission and telemetry work. Telemetry loss alone does not imply pilot-command loss.

## 3. Interfaces and Data Contracts

These are logical contracts. Concrete types, protocols, numeric units, timing, and electrical properties require the external decisions in Section 5.

| Contract | Required content and behavior | TBD items |
|---|---|---|
| Sensor sample | Source ID; value(s); declared units/scaling/sign; monotonic timestamp or documented alignment metadata; sequence/order where available; validity; rejection/fault reason; interface status. Missing, stale, out-of-range, implausible, or invalid samples remain explicitly invalid. | Devices, protocols, units, ranges, rates, timestamp source, age limits, physical plausibility and detection thresholds. |
| Estimate | State variables required by the active mode; units and reference frame; source/availability; validity or confidence; timestamp/age; estimator fault status. Invalid inputs produce invalid estimates, not stale plausible outputs. | Estimator algorithm, frame conventions, sensor alignment, confidence semantics, latency and validity limits. |
| Pilot command / setpoint | Parsed command identity and mode; source/sequence/time; validity and rejection reason; declared units; bounded mode-specific setpoint. Invalid, stale, missing, malformed, or out-of-range input follows an approved behavior and cannot bypass limiters. | Link/protocol, authentication/pairing, ranges, freshness budgets, mappings, and invalid-command policy. |
| Flight configuration | Schema/version and identity; supported hardware/sensors/modes; limits and calibration parameters; source/provenance; validation result and diagnostics. Missing or invalid safety-critical values inhibit the affected function/startup; protected values are immutable while armed. | Schema, allowed values, protected fields, provisioning, integrity mechanism, and per-field inhibit behavior. |
| Startup/readiness status | Startup state; per-configured-component initialization and supported self-test result; calibration status where applicable; ready/inhibit state and reason. A critical failure cannot be reported as ready or satisfy arming. Expose status to the configured GCS or pilot interface. | Startup ordering, configured check inventory, criticality mapping, readiness criteria, calibration applicability/procedure, report protocol and timing, and behavior if the selected reporting interface is unavailable during startup. |
| Control demand / actuator command | Bounded demand, allocation result, saturation status, channel identity, configured ESC range, validity, and disarmed inhibit behavior. Invalid demand cannot produce unbounded output. | Coordinate/sign conventions, mixer, motor order/direction, output protocol/rate/ranges, inhibit value, timeout and ESC feedback. |
| Fault/status event | Stable fault identity; detection time; source; severity; selected approved response; active safety mode; recovery condition/state; operator-visible reason. Arbitration is deterministic for configured concurrent faults. | Fault table, severity, priority, approved response, recovery, timing, and persistence requirements from hazard analysis. |
| Health/telemetry message | Supported fields reflect current internal state; schema/version; malformed and unsupported messages are rejected; interface failures are reported. Telemetry loss does not change control when pilot command remains valid. | Physical/logical interface, message formats, fields, rates, error model, authentication, and loss behavior. |
| Log record | Event type, timestamp or ordering counter, relevant mode/fault/status, and storage result. Storage-full and unavailable storage behavior is explicit; logging load is bounded; sensitive or unsafe control inputs are not exposed. | Event schema, clock source, storage capability, retention, persistence, and timing budget. |
| Timing/health measurement | Cycle frequency, execution time, end-to-end latency, deadline/overload/watchdog status, and observable reset state. Misses reach the safety path within the approved budget. | Processor/RTOS, scheduler, control rate, budgets, supported worst-case load, monitor independence, watchdog, and reset response. |

All data contracts distinguish **valid**, **invalid**, **missing**, and **unsupported/not installed** where applicable. A consumer must check status and age before use. No interface silently coerces invalid data into a usable value.

For SF-006, the validator evaluates each configured sample against its configured freshness and physical-plausibility criteria and publishes an explicit validity result and rejection reason/status. Fresh, in-range data may be valid; stale, missing, invalid, out-of-range, or otherwise implausible data is not consumable as valid, including when its numeric value is zero. Zero itself is not an invalidity rule: classification follows the configured sensor criteria and explicit status. Detection timing is measured against configured timing inputs, not an assumed universal deadline. Fault reporting and downstream mode inhibition or degraded response consume this status but are selected only under the applicable approved policy.

## 4. State and Safety Behavior

### Conceptual states

The following are design-level states, not a finalized aircraft state machine: **Power-off**, **Initialization**, **Standby/Disarmed**, **Arming evaluation**, **Armed/Ready**, a configured supported flight mode, **Degraded/Failsafe**, and a configured landing or emergency state where supported. Exact state names, events, transition priorities, entry/exit conditions, and recovery are TBD and require the approved mode and hazard baselines.

- Initialization is deterministic. A critical startup/configuration/interface check failure keeps the system not-ready and disarmed and exposes the inhibit reason. Calibration occurs only under its declared procedure.
- Arming is accepted only when every configured gate passes using current valid status. Each failed gate has a reason. Stale/invalid status cannot satisfy a gate, and prohibited/conflicting transitions are rejected deterministically.
- The actuator boundary holds every channel at the configured inhibit value in Standby/Disarmed regardless of pilot setpoint. Disarming restores inhibition deterministically. Arming does not itself authorize a particular flight mode or remove other output bounds.
- Mode entry and continued operation require configured prerequisites. Altitude Hold requires a valid configured altitude estimate; Position Hold requires valid position and velocity; RTL requires valid home/navigation and configured route prerequisites. Unsupported features are reported unsupported, not treated as passing gates.
- Invalid flight-critical state causes the configured mode inhibit/exit or approved degraded/failsafe action. Temporary and sustained navigation loss may have distinct behavior only where approved. No generic motor-stop behavior is assumed safe.
- SF-006 status is a prerequisite input to SF-007 arming gates and downstream estimation/mode logic: stale or invalid status cannot satisfy an arming or mode prerequisite. This supports FCS-S-001 through SF-007; FCS-S-005 is a related downstream constraint that a single detected sensor fault must not cause unbounded control output. Neither requirement authorizes a particular sensor-fault response; response selection remains governed by hazard-approved policy.
- Fault severity, simultaneous-fault arbitration, response, and recovery are sourced from aircraft hazard analysis. Safety actions preempt mission/telemetry work. Critical faults do not recover automatically unless explicit conditions are defined and satisfied.
- Watchdog reset or unrecoverable software fault enters the defined safe/degraded behavior; reset/restart state is observable and never spuriously arms. Loss of each power input and brownout require aircraft-specific behavior.
- Takeoff, landing, touchdown, and disarming follow an approved output sequence. Automatic in-flight disarm is prohibited unless explicitly required by the approved safety concept. Hardware motor-output checks are propeller-off under approved procedures.

## 5. Configuration and External Decisions

Configuration validation is fail-closed for the affected safety-critical function: validate schema/version, required fields, types, supported-feature compatibility, configured ranges, and protected parameters before use; provide a diagnostic; prohibit protected runtime changes while armed. The schema and exact rejection/startup policy are not yet defined. No target parameter is assigned by this design.

| Decision / evidence needed | Affected stories and design elements | Needed from |
|---|---|---|
| Approved startup sequence; configured check inventory and criticality; readiness criteria/reporting; applicable sensor calibration procedures; reporting behavior when the selected GCS/pilot interface is unavailable during startup | SF-001, SF-003-SF-008; startup/readiness manager, configuration gate, arming gate, status interface | Platform and device owners for supported checks/interfaces and reporting-path availability; sensor owners for calibration procedures; project/safety authority for criticality, readiness criteria, and any alternate or fallback reporting behavior |
| Aircraft/airframe, motor count/layout, motor order/direction, operating environment and mission | SF-001, SF-014, SF-023, SF-026, SF-029, SF-030, SF-035; allocation, envelope and safety | Aircraft/project baseline and system engineering |
| Supported modes, installed sensors, redundancy, and per-mode source requirements | SF-001, SF-004, SF-018, SF-020-SF-026, SF-029; startup and mode gates | Product/aircraft requirements authority |
| Processor, RTOS, board, electrical interfaces, compiler/toolchain, target build | SF-001, SF-002, SF-004, SF-010, SF-017, SF-035; adapters, build identity and scheduler | Hardware and firmware platform owners |
| Configuration schema, ranges, protected parameters, provisioning/integrity and invalid-value policy | SF-003, SF-004, SF-007, SF-013, SF-014, SF-023, SF-024, SF-028; config gate | Configuration owner and safety authority |
| Sensor/ESC protocols, units, scaling, sign/frame, rates, ranges, timestamps, calibration, timeouts, and feedback availability | SF-004-SF-006, SF-012, SF-014, SF-020, SF-026, SF-035; device/data contracts | Selected device datasheets and interface owners |
| Per-sensor freshness and plausibility limits, fault thresholds, flight-critical classification, allocated detection budget, and detection-event/clock semantics | SF-005-SF-007, SF-012, SF-019, SF-020; sensor validator, health/fault status, estimator and prerequisite gates | Sensor/interface owners provide characterization and timestamp semantics; aircraft safety and timing authorities allocate criticality and detection budgets |
| Command and telemetry protocols, message schemas, ranges, freshness, authentication/pairing, update rates, error/loss behavior | SF-011, SF-027, SF-031; parsers and link monitors | GCS/radio and communication interface owners |
| Numerical flight envelope, setpoint/rate limits, altitude/speed/geofence, battery characteristics/thresholds | SF-013, SF-021-SF-023, SF-028, SF-029; limiters and threshold monitors | Aircraft performance baseline, battery supplier, safety authority |
| Estimator algorithm, sensor alignment/fusion, confidence/validity semantics, and latency limits | SF-005, SF-006, SF-012, SF-020-SF-022, SF-029 | Estimation/control engineering and sensor characterization |
| Controller design, gains, loop rates, attitude/rate/hold performance criteria | SF-015-SF-017, SF-021, SF-022; control loops and acceptance tests | Control engineering and aircraft dynamics evidence |
| Scheduler, worst-case load, cycle/latency budgets, deadline monitor, watchdog and reset behavior | SF-001, SF-010, SF-017, SF-031-SF-035 | Platform design and timing analysis |
| Hazard analysis, fault severity/priority, approved per-fault responses, recovery, power loss/brownout behavior | SF-001, SF-007, SF-009, SF-019, SF-026-SF-030, SF-033-SF-035 | Aircraft safety authority; approved FHA/FMEA/FTA or equivalent |
| Mission schema/capabilities and pause/abort behavior; RTL home/route/altitude/termination; takeoff/touchdown criteria and output sequence | SF-021-SF-026, SF-029; optional mode services | Product/operations and safety authorities |
| Storage, event schema, clock, retention, persistence, and diagnostic privacy boundaries | SF-031, SF-032, SF-034, SF-035 | Platform/storage and data governance owners |
| HIL/bench setup, interface test procedure, target acceptance values, and applicable operational/standards basis | SF-002, SF-034, SF-035 and target acceptance generally | Verification authority and project compliance owner |

Until these are approved, stories may implement interfaces, deterministic fakes, and decision-independent logic, but cannot claim target acceptance for decision-dependent behavior.

## 6. Requirements Traceability

Verification shorthand: **UT** unit test; **SIL** software-in-loop; **FI** deterministic fault injection; **HIL/B** hardware-in-loop or propeller-off bench under approved procedures; **I/A** inspection or analysis. These are planned evidence types, not completed verification results.

Requirement ID ranges in the tables are inclusive; for example, `FCS-F-001-F-004` means FCS-F-001 through FCS-F-004.

| Story | Cited requirements | Design element | Planned verification evidence |
|---|---|---|---|
| SF-001 | FCS-NF-010, FCS-NF-011; SRS sections 8-10 | Module boundaries, logical contracts, source-to-design traceability; TBD inputs remain visible | I/A: interface, ownership, units/status/timing/error contracts and trace links; review TBDs |
| SF-002 | FCS-NF-012 | Build/configuration identity at startup and in test evidence | Clean-checkout build and repeated-build comparison per declared result; UT missing/invalid identity |
| SF-003 | FCS-F-005, FCS-F-006, FCS-S-012, FCS-NF-013, FCS-T-008 | Fail-closed configuration gate and armed-state protection | UT valid/missing/malformed/unsupported/range cases, diagnostics, armed mutation rejection; FI T-008 |
| SF-004 | FCS-F-001-F-004, FCS-F-007, FCS-F-008 | Startup/readiness manager; configured sensor/actuator initialization; supported self-test results; observable readiness/inhibit status; declared calibration procedure | UT/SIL deterministic sequencing; inject pass and each configured critical-check failure; verify all configured interfaces initialize before ready, failure prevents readiness/arming, and status/reason is observable via the selected GCS or pilot interface; verify calibration follows its declared procedure. If that reporting interface is unavailable during startup, acceptance of the required observable reason is blocked until its behavior is decided. |
| SF-005 | FCS-F-010, FCS-F-011, FCS-F-013 | IMU adapter and timestamp/alignment contract | UT conversion/scaling/order/timeout/interface errors; measure configured sample rate/age; health-path injection |
| SF-006 | FCS-F-012, FCS-F-019, FCS-S-004, FCS-T-001, FCS-T-002 | Per-configured-sensor freshness/plausibility validator; explicit valid/invalid/missing status and rejection reason; status consumed by estimator and safety/mode prerequisites | UT separately inject fresh/in-range, stale, missing, invalid, out-of-range, and implausible samples; verify reason/status preservation and that invalid data cannot satisfy a consumer prerequisite (including a numeric-zero sample with explicit status). FI T-001: stopped-updating IMU is detected and affected modes are inhibited or the approved degraded response selected. FI T-002: configured-range exceedance is rejected/invalid and fault-reported. Measure detection timing against approved configured budgets; timing and response assertions remain blocked pending decisions. |

| SF-007 | FCS-F-060-F-062, FCS-S-001 | Arming state machine and reasoned gates | UT normal/rejected/conflicting transitions, stale prerequisite and each failed-gate reason |
| SF-008 | FCS-F-063, FCS-S-001 | Actuator-side disarmed inhibit independent of setpoint | UT/integration all channels inhibited for arbitrary setpoints; arm eligibility after gates; deterministic disarm |
| SF-009 | FCS-F-072, FCS-F-073, FCS-F-080, FCS-S-009, FCS-S-013, FCS-T-012 | Fault classification, approved response lookup, deterministic arbiter | FI single/simultaneous faults including T-012; verify approved priority, active reason, safety preemption |
| SF-010 | FCS-NF-001, FCS-NF-003, FCS-NF-008, FCS-NF-009, FCS-S-007, FCS-S-008, FCS-T-009, FCS-T-010 | Deadline/overload/watchdog monitor and reset state | SIL/target FI T-009/T-010; measure detection/response against configured budgets; verify no spurious arm |
| SF-011 | FCS-F-050-F-052, FCS-F-038 | Command parser/validator and mode-specific mapping | UT valid, malformed, stale, missing, range and mapping; invalid command cannot bypass limits |
| SF-012 | FCS-F-014, FCS-F-020, FCS-F-021, FCS-F-024 | Attitude/rate estimator with validity and latency | Deterministic reference-vector UT/SIL; invalid/stale input; units/status and configured latency |
| SF-013 | FCS-F-032, FCS-F-033, FCS-F-039, FCS-S-006 | Setpoint bounds, transition limiter, saturation status | UT at/below/above limits, abrupt changes, invalid limits, deterministic output/status |
| SF-014 | FCS-F-034, FCS-F-035, FCS-F-037, FCS-S-005, FCS-S-006 | Validated allocation, ESC range limiter, disarmed contract | UT declared mixer vectors, invalid geometry/input, bounds and saturation; propeller-off check when approved |
| SF-015 | FCS-F-030, FCS-F-036 | Rate controller with integral protection | UT/SIL direction/response and saturation anti-windup; invalid state/setpoint; project performance criteria TBD |
| SF-016 | FCS-F-031 | Attitude loop to bounded rate demand | SIL attitude-error direction, configured limits, invalid-estimate inhibit/degraded behavior |
| SF-017 | FCS-NF-001 through FCS-NF-003, FCS-NF-008, FCS-NF-014 | Deterministic cycle scheduler and bounded lower-priority work | Instrument cycle frequency, worst-case execution and end-to-end latency under representative maximum load; timing fault reaches SF-010 |
| SF-018 | FCS-F-020, FCS-F-052; SRS section 5 | Supported-mode state machine and entry/exit gates | UT allowed/prohibited/repeated transitions, invalid state, mode/reason reporting |
| SF-019 | FCS-F-025, FCS-F-076, FCS-F-079, FCS-S-003, FCS-S-005, FCS-S-008, FCS-S-010, FCS-S-014 | Fault-driven degraded/failsafe selector and active safety status | FI critical input loss, competing fault, unavailable-navigation case; recovery only under approved conditions |
| SF-020 | FCS-F-015-FCS-F-018, FCS-F-022, FCS-F-023 | Configured altitude/navigation source adapters and estimate validity | UT each installed/absent/invalid source; magnetometer validation; expose per-mode availability/confidence |
| SF-021 | FCS-F-040, FCS-F-041 | Altitude Hold prerequisite gate and bounded regulation | UT reject invalid/absent altitude; SIL valid regulation and approved transition on loss; numeric criteria TBD |
| SF-022 | FCS-F-042, FCS-F-043, FCS-F-045 | Position Hold prerequisite and navigation degradation handling | UT invalid entry; SIL bounded valid response; FI T-003 and temporary/sustained loss behavior per approved policy |
| SF-023 | FCS-F-044 | Enabled altitude/speed/geofence constraints with source-validity gates | UT boundaries/exceedances and unavailable data; disabled/not-installed reports unsupported |
| SF-024 | FCS-F-053, FCS-F-055 | Mission schema/capability/constraint validator | UT valid, malformed, unsupported, constraint violations and reason; acceptance does not start execution or arm |
| SF-025 | FCS-F-054, FCS-F-056 | Mission sequencing, pause/abort and progress state | SIL command order/progress; pause/abort per supported state; safety-event preemption and termination reason |
| SF-026 | FCS-F-064-FCS-F-067 | Optional takeoff/landing/touchdown state path and motor-output sequencing | SIL nominal/interrupted/invalid flows; approved output sequence; propeller-off bench only; no unapproved in-flight disarm |
| SF-027 | FCS-F-070, FCS-F-074, FCS-S-002, FCS-S-003, FCS-T-004 | Independent pilot-command link monitor and approved response | FI disconnect/timeout/invalid/recovery; measure T-004 detection budget; telemetry loss must not trigger command-loss policy |
| SF-028 | FCS-F-071, FCS-F-075, FCS-T-006, FCS-T-007 | Battery measurement validation and warning/critical policy | UT below/at/above and invalid/missing values; FI T-006/T-007; thresholds/responses from approved config |
| SF-029 | FCS-F-090-FCS-F-093 | Optional RTL prerequisite, route, termination and navigation-loss state | UT invalid home/navigation and unsupported RTL; SIL configured route/termination and mid-route loss response |
| SF-030 | FCS-F-094, FCS-S-003, FCS-S-008, FCS-S-011 | Hazard-approved emergency selector and power-fault handling | I/A trigger-to-approved-response rationale; FI priority/active status and supported brownout/power cases |
| SF-031 | FCS-F-077, FCS-F-100, FCS-F-101, FCS-F-104-FCS-F-106, FCS-NF-015, FCS-T-005 | Health publisher, protocol validation, telemetry/command separation | Protocol UT valid/malformed/unsupported/interface error; FI T-005; verify telemetry load and loss do not alter valid control |
| SF-032 | FCS-F-078, FCS-F-102, FCS-F-103, FCS-NF-014, FCS-NF-015 | Bounded timestamped/ordered event log | UT order/timestamps/content/full-storage and persistence where supported; analysis of load/privacy constraints |
| SF-033 | FCS-F-080, FCS-S-009, FCS-S-013, FCS-T-012 | System-level simultaneous/cascading fault scenarios | Repeatable FI for approved combinations; assert selected response/reason, safety priority and no unavailable navigation use |
| SF-034 | FCS-T-001-FCS-T-012; SRS section 11 | Deterministic SIL/fault-injection regression harness and requirement-tagged results | Automated asserted outcomes, fixed random seeds, reproducible run; identify unsupported hardware-only checks as not run |
| SF-035 | FCS-F-002, FCS-F-003, FCS-F-013, FCS-F-035, FCS-NF-001 through FCS-NF-009; SRS section 11 | Target HIL/propeller-off interface, startup, timing and fault verification | Approved target procedures and pass/fail records; propellers removed for actuator checks; flight tests excluded |

### Traceability limitations
- Cross-story safety verification must also show invalid/stale status cannot satisfy SF-007 arming prerequisites (FCS-S-001), while SF-019/SF-014 preserve the constraint that a single sensor fault cannot cause unbounded control output (FCS-S-005); these are related requirements, not additional SF-006 citations.

- SF-035 cites FCS-NF-001 through FCS-NF-009, but the backlog's acceptance checks do not define target evidence for every physical/environmental requirement (notably power, temperature/vibration, and electromagnetic environment) or provide numeric limits. These remain TBD and require appropriate analysis/qualification; they are not demonstrated by generic SIL evidence.
- The SRS calls for command/telemetry authentication or pairing where applicable, but no story defines a security protocol or acceptance criteria. This is an open interface/security requirement, not an implied implementation choice.
- For SF-006, classification and invalid-status propagation have unit-testable oracles from the story and FCS-F-012/FCS-F-019. A numeric detection-time pass criterion is not available: FCS-S-004 requires an allocated detection time, but no per-sensor allocation, flight-criticality list, clock semantics, or detection start/end event is supplied. FCS-T-001 permits affected-mode inhibition or an approved degraded response; that expected response is unresolved until the applicable aircraft policy is approved. FCS-T-002 does define rejection/invalid handling and fault reporting for configured-range exceedance, but its range and threshold values remain TBD.
- FCS-T-003 and FCS-T-011 are conditional on configured GNSS/Position Hold and available ESC/motor feedback respectively. Absent hardware/features must be reported unsupported/not applicable, never passed as if tested.
- FCS-T-001 through FCS-T-012 in SF-034 are covered only for implemented and configured features. Hardware-only evidence remains not run until target hardware and approved procedures exist.

## 7. Verification Strategy

Use the backlog order: unit tests first, then deterministic SIL, then HIL/bench checks where target interfaces and approved procedures exist. Every result identifies software revision, target/configuration identity, story ID, requirement/test ID, inputs, and pass/fail criteria. Fixed seeds are used for randomized cases; expected outcomes are asserted, not merely logged.

| Verification slice | Evidence to collect | Stories / requirement IDs |
|---|---|---|
| Configuration/startup | Valid and each invalid configuration class; deterministic approved startup sequence; initialization of configured sensor/actuator interfaces; supported self-tests; injected passing and each configured critical check; readiness/inhibit reason visible at the selected GCS or pilot interface; declared calibration procedure | SF-002-SF-004; FCS-F-001-FCS-F-008, FCS-NF-012-FCS-NF-013, FCS-T-008. Startup order, check criticality, readiness criteria, calibration procedure, and reporting behavior during loss of the selected status interface are decision-dependent; target acceptance is blocked until baselined. |
| Sensors/state | UT sample matrix: fresh/in-range; stale; missing; invalid; configured-range exceedance; other configured implausibility; preserve rejection reason/status; distinguish explicitly invalid numeric zero from a valid zero when configuration permits; show invalid status cannot satisfy a downstream prerequisite. FI T-001 stopped IMU updates and T-002 range exceedance. Keep validator classification assertions separate from consumer response assertions. | SF-005, SF-006, SF-012, SF-020; FCS-F-010-FCS-F-024, FCS-S-004, FCS-T-001-FCS-T-003. SF-006 detection-time assertions require the approved per-sensor budget and timing-event definition; T-001 response assertions require the approved mode/fault policy. |
| Arming/output | Gate transitions and reasons, stale prerequisites, disarmed output for arbitrary setpoints, bounded mixer output and saturation | SF-007, SF-008, SF-014; FCS-F-060-FCS-F-063, FCS-F-034-FCS-F-037, FCS-S-001, FCS-S-005-FCS-S-006 |
| Command/control/modes | Command parser boundaries, setpoint bounds/rates, controller direction/anti-windup, mode gates and invalid-state behavior | SF-011, SF-013, SF-015, SF-016, SF-018; relevant FCS-F-030-FCS-F-039, FCS-F-050-FCS-F-052 |
| Timing/runtime | Cycle frequency, WCET, end-to-end latency, representative maximum load, deadline/overload/watchdog injection, restart state | SF-010, SF-017; FCS-NF-001 through FCS-NF-003, FCS-NF-008-FCS-NF-009, FCS-S-007-FCS-S-008, FCS-T-009-FCS-T-010 |
| Fault and link response | Single and simultaneous faults, command-link loss, battery thresholds, sensor loss, recovery gate, reason/reporting | SF-009, SF-019, SF-027, SF-028, SF-033; FCS-F-070-FCS-F-080, FCS-S-002-FCS-S-004, FCS-S-008-FCS-S-014, FCS-T-004, FCS-T-006-FCS-T-007, FCS-T-012 |
| Optional modes/mission | Unsupported-source gates, valid/invalid altitude and navigation, envelope constraints, mission validation/order/pause/abort, RTL and landing scenarios | SF-021-SF-026, SF-029; FCS-F-040-FCS-F-045, FCS-F-053-FCS-F-056, FCS-F-064-FCS-F-067, FCS-F-090-FCS-F-093 |
| Communications/logging | Malformed/unsupported messages, telemetry loss with command valid, event order/storage-full/persistence, bounded load | SF-031, SF-032; FCS-F-077-FCS-F-078, FCS-F-100-FCS-F-106, FCS-NF-014-FCS-NF-015, FCS-T-005 |
| Target integration | Configured sensor/ESC startup and interface checks, timing, fault injections, build/configuration identity | SF-002, SF-004, SF-005, SF-010, SF-014, SF-017, SF-034, SF-035; applicable FCS-F-002, FCS-F-003, FCS-F-013, FCS-F-035 and FCS-NF-001 through FCS-NF-009 |

### Document Verification Status

| Check | Result | Limitation |
|---|---|---|
| Backlog story coverage | SF-001 through SF-035 each have a traceability row with cited requirements, design elements, and planned evidence. | Traceability does not demonstrate that a requirement is satisfied. |
| Requirement applicability and gaps | Conditional features and known evidence gaps are identified in the traceability limitations and decision register. | Target acceptance remains blocked until applicable decisions and criteria are approved. |
| Verification evidence | Unit, SIL, fault-injection, and HIL/bench activities in this document are plans, not reported results. | No software tests, SIL, fault-injection, HIL, or target checks were run for this document update. |

### Design Validation: Desk Review

At document level, the logical responsibilities and data flow are coherent with the backlog: validity and freshness are explicit at interfaces; invalid status cannot satisfy mode or arming gates; disarmed outputs remain inhibited; safety actions preempt mission and telemetry work; and optional functions remain conditional. No aircraft-specific numerical value, protocol, mixer, controller gain, fault priority, or failsafe response is selected here.

This is a desk review of document completeness and internal consistency only. It does not validate aircraft behavior, safety, performance, hardware, or operational readiness. The following validation questions remain open:

- Which modes, sensors, hardware, and numerical acceptance limits are approved for the target aircraft?
- What hazard-approved fault responses, priorities, and recovery conditions govern each configured fault?
- How will the SF-008/SF-014 actuator-contract dependency cycle be resolved while preserving the disarmed inhibit requirement?
- What target procedures and evidence will close the environmental, power, EMC, communication-security, and storage-related gaps identified above?

HIL and actuator bench work requires selected target hardware, known interface specifications, approved procedures, and propellers removed for motor-output checks. This design does not authorize flight testing. No target-level pass can be claimed before aircraft decisions and acceptance limits are baselined.

## 8. Dependencies and Design Risks

### Delivery dependencies

- Foundation and safety gates: `SF-001 -> SF-003/SF-004/SF-005 -> SF-006/SF-007/SF-009`.
- SF-006's explicit backlog dependency is SF-005, which supplies the configured, timestamped/aligned IMU sample contract. Validated configuration and configured startup/readiness from SF-003/SF-004 are upstream context for target behavior, but are not listed as SF-006 story dependencies. SF-006 is then a prerequisite for SF-007 arming gates, SF-012 estimation, SF-019 fault-driven response, and SF-020 optional navigation estimates; invalid status must propagate without these consumers reclassifying it as valid.
- Core controlled flight: `SF-006/SF-007 -> SF-011/SF-012/SF-013 -> SF-014/SF-015/SF-016/SF-017/SF-018 -> SF-019`.
- Optional navigation and higher-level functions: `SF-006 -> SF-020 -> SF-021/SF-022/SF-023 -> SF-024 -> SF-025`; RTL `SF-029` additionally requires approved navigation and route behavior.
- Safety and regression convergence: `SF-009/SF-019 -> SF-027/SF-028/SF-030/SF-033 -> SF-034 -> SF-035` (with the explicit story dependencies in the backlog controlling exact sequencing).
- SF-008 depends on SF-007 and the SF-014 output contract; SF-014 depends on SF-008 and SF-013. This is a contract-level dependency cycle: define the actuator inhibit/output contract and test seam in SF-001/SF-014 early, then integrate the arming gate and output eligibility without weakening either story's acceptance checks.

### Principal design risks and open issues

| Risk / issue | Consequence | Required resolution or evidence |
|---|---|---|
| Hazard analysis and response table are absent | A generic failsafe, emergency stop, recovery, or fault priority could be unsafe | Approve fault severity, response, priority, and recovery for the target before enabling SF-009, SF-019, SF-027-SF-030, or SF-033 |
| No numerical limits or timing budgets are baselined | Bounds, freshness, detection, latency, control performance, and timing tests cannot have target pass criteria | Populate the project-specific parameter set and trace each value to aircraft analysis, supplier data, or approved safety evidence |
| Target interfaces and configuration schema are undecided | Drivers, scaling, inhibit values, startup readiness, and config rejection behavior cannot be finalized | Select hardware/protocols and approve interface/configuration contracts before target acceptance |
| Mode and sensor availability are conditional | Navigation/missions/RTL/hold functions may be unsupported, and invalid data could be mistakenly treated as a satisfied prerequisite | Baseline installed sensors and enabled modes; exercise absent-source behavior explicitly |
| Fault and timing monitoring depend on platform capabilities | Detection independence, watchdog response, reset safety, and priority under load remain unproven | Complete platform design, scheduler/WCET analysis, and watchdog/reset safety review |
| Acceptance criteria under-specify some cross-cutting requirements | Referencing FCS-NF-001-FCS-NF-009 does not by itself define evidence for environmental, EMC, or power qualification | Add target-specific procedures, limits, and acceptance evidence to SF-035 planning |
| Communications security and storage behavior lack concrete contracts | Message trust, telemetry behavior, event persistence, and privacy cannot be verified fully | Define applicable authentication/pairing, supported fields, storage/retention, and error policies |

This design records intended logical behavior only. Any change to aircraft configuration, supported modes, safety responses, or acceptance values requires corresponding configuration identity, requirement trace updates, and verification evidence.