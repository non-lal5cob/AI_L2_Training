# Software and Firmware Story Backlog

**Source baseline:** [Drone Flight Control System Requirements](drone_flight_control_system_requirements.md) (DFC-SRS-001, v1.0)  
**Purpose:** Prioritized, independently verifiable software and firmware work for the training baseline.

## Backlog rules

- Priority is a delivery order: **P0** is the software foundation and safety gates; **P1** is core controlled-flight capability; **P2** is optional navigation, mission, and integration capability. Dependencies take precedence over priority labels.
- Size uses relative effort: **S** (small), **M** (medium), **L** (large but bounded). No story is larger than L. Split a story during refinement if it cannot be completed and verified within L.
- Every story has its own acceptance checks and can be verified without requiring a later story to be complete. Hardware-dependent checks may use deterministic fakes or SIL until the target interface exists.
- A dependency marked **Decision** is an aircraft/project input, not a software story. Do not invent its value in implementation. A story depending on an unresolved decision may develop test seams, but cannot claim target acceptance.
- Run unit tests first, then SIL, then HIL/bench checks as applicable. Propeller-off bench work and approved procedures are required before any hardware motor-output testing. This backlog does not authorize flight testing.

## External decisions and enabling inputs

Resolve and baseline the applicable inputs before accepting target-specific behavior: aircraft/airframe and motor layout; supported modes and sensor set; processor, RTOS, and interface hardware; sensor and ESC protocols, units, rates, ranges, and timeouts; numerical flight and timing limits; battery characteristics and thresholds; fault severity and aircraft-approved responses from hazard analysis; and applicable operational constraints. These inputs are required by the stories below as indicated in dependencies. See sections 9, 10, and 14 of DFC-SRS-001.

## P0: Software foundation and safety gates

### SF-001 - Baseline firmware interfaces and safety assumptions

- **Size:** M
- **Requirements:** FCS-NF-010, FCS-NF-011; sections 8-10
- **Depends on:** Decision: supported hardware, modes, sensor/actuator interfaces, timing budgets, and initial hazard-analysis outputs.
- **Story:** As a firmware developer, I need documented module boundaries and interface contracts so each flight function can be implemented and verified independently.
- **Acceptance checks:** Driver, estimation, control, mode, safety, and communication interfaces identify data units, validity, ownership, update timing, and error behavior; requirement IDs map to software modules and verification methods; TBD aircraft values remain explicitly unresolved rather than receiving assumed defaults.

### SF-002 - Reproducible firmware build and configuration identity

- **Size:** S
- **Requirements:** FCS-NF-012
- **Depends on:** SF-001; Decision: selected compiler/toolchain and target build environment.
- **Story:** As a maintainer, I need a repeatable build with an identifiable software/configuration version so test results can be reproduced.
- **Acceptance checks:** A clean checkout builds using documented commands; the build identifies source revision, target, and configuration; repeating the build with the same inputs produces the declared reproducibility result; a test verifies invalid or missing build identity is reported.

### SF-003 - Validate safety-critical flight configuration

- **Size:** M
- **Requirements:** FCS-F-005, FCS-F-006, FCS-S-012, FCS-NF-013, FCS-T-008
- **Depends on:** SF-001; Decision: configuration schema, valid ranges, and protected parameters.
- **Story:** As the FCS, I need to reject missing, malformed, unsupported, or out-of-range configuration before it can affect flight behavior.
- **Acceptance checks:** Unit tests cover valid configuration and each invalid class; invalid configuration inhibits the affected function or startup as defined and provides a diagnostic; configuration cannot be changed through runtime inputs while armed; no invalid value silently falls back to a usable control value.

### SF-004 - Startup checks and readiness reporting

- **Size:** L
- **Requirements:** FCS-F-001 through FCS-F-004, FCS-F-007, FCS-F-008
- **Depends on:** SF-001, SF-003; sensor and actuator interface contracts; Decision: startup sequence, calibration policy, and readiness criteria.
- **Story:** As a pilot, I need startup to initialize and check configured components and report readiness so arming is permitted only after required checks pass.
- **Acceptance checks:** Startup sequencing is deterministic; tests inject a passing check and each configured critical-check failure; a critical failure prevents readiness and arming; readiness/inhibit reason is observable; supported calibration follows its declared procedure.
- **Subtasks:** Define startup states and check results; implement component initialization and calibration hooks; test success, failure, and readiness reporting.

### SF-005 - Acquire and time-align configured IMU data

- **Size:** L
- **Requirements:** FCS-F-010, FCS-F-011, FCS-F-013
- **Depends on:** SF-001; Decision: IMU device/protocol, sample rate, units, timestamp source, and maximum data age.
- **Story:** As the estimator, I need timestamped, consistently scaled IMU samples so rate and attitude estimates consume coherent inputs.
- **Acceptance checks:** Driver tests cover valid samples, conversion/scaling, ordering, timeout, and interface error; samples expose a monotonic timestamp or documented time-alignment metadata; sample rate and age are measured against configured values; injected communication failure is surfaced to the health path.
- **Subtasks:** Implement the driver abstraction and sample representation; implement configured acquisition and timestamping; test conversion, timing, and injected interface failures.

### SF-006 - Validate sensor sample freshness and plausibility

- **Size:** M
- **Requirements:** FCS-F-012, FCS-F-019, FCS-S-004, FCS-T-001, FCS-T-002
- **Depends on:** SF-005; Decision: per-sensor physical ranges, freshness limits, and fault thresholds.
- **Story:** As a flight function, I need invalid, stale, missing, or implausible sensor samples explicitly marked invalid so they cannot be consumed as valid data.
- **Acceptance checks:** Tests cover fresh/in-range, stale, missing, out-of-range, and invalid samples; rejected samples retain a reason/status; downstream consumers can distinguish invalid input from a valid numeric zero; configured detection timing is measured.

### SF-007 - Implement arming state and reasoned safety gates

- **Size:** L
- **Requirements:** FCS-F-060, FCS-F-061, FCS-F-062, FCS-S-001
- **Depends on:** SF-003, SF-004, SF-006; Decision: approved arming conditions and transition rules.
- **Story:** As a pilot, I need explicit arming states and a reason for each inhibit so motors can be enabled only when configured safety conditions pass.
- **Acceptance checks:** State-transition tests cover disarmed, arming request, armed, disarm request, and rejected transitions; every failed gate reports its reason; stale or invalid prerequisite status cannot satisfy a gate; transition priority and prohibited transitions are tested.
- **Subtasks:** Define state/event model and gate interface; implement transitions and inhibit reasons; test normal, rejected, and conflicting requests.

### SF-008 - Enforce motor inhibition while disarmed

- **Size:** S
- **Requirements:** FCS-F-063, FCS-S-001
- **Depends on:** SF-007; SF-014 actuator output contract.
- **Story:** As the FCS, I need disarmed motor outputs held at the configured inhibit value so no control request can cause unintended motor activation.
- **Acceptance checks:** Unit and integration tests verify all motor channels remain inhibited for any pilot setpoint while disarmed; arming transition changes output eligibility only after all gates pass; disarming restores inhibition deterministically.

### SF-009 - Define fault severity and arbitration behavior

- **Size:** M
- **Requirements:** FCS-F-072, FCS-F-073, FCS-F-080, FCS-S-009, FCS-S-013, FCS-T-012
- **Depends on:** SF-001; Decision: hazard analysis, fault-severity table, approved responses, and simultaneous-fault priority.
- **Story:** As the safety manager, I need each detected fault classified and arbitrated consistently so concurrent faults select the approved response.
- **Acceptance checks:** Each configured fault maps to severity, response, and recovery policy; tests inject single and simultaneous faults and verify deterministic selected response and active reason; safety actions take precedence over mission and telemetry work; no unapproved automatic recovery is accepted.

### SF-010 - Monitor execution deadlines and watchdog state

- **Size:** M
- **Requirements:** FCS-NF-001, FCS-NF-003, FCS-NF-008, FCS-NF-009, FCS-S-007, FCS-S-008, FCS-T-009, FCS-T-010
- **Depends on:** SF-001; Decision: processor/RTOS, control timing budgets, watchdog design, and approved reset response.
- **Story:** As the FCS, I need to detect deadline misses, overload, and watchdog events so execution failure enters the defined degraded or safe behavior.
- **Acceptance checks:** SIL or target tests inject deadline miss, overload, and watchdog/reset conditions; detection and response meet configured limits; reset/restart state is observable and does not spuriously arm; safety handling preempts non-critical work.

## P1: Core controlled-flight software

### SF-011 - Receive and validate pilot commands

- **Size:** M
- **Requirements:** FCS-F-050, FCS-F-051, FCS-F-052, FCS-F-038
- **Depends on:** SF-001; Decision: pilot-link protocol, command ranges, freshness limits, and invalid-command behavior.
- **Story:** As the control system, I need to validate and map fresh pilot inputs into mode-specific setpoints so malformed or stale commands cannot directly affect control.
- **Acceptance checks:** Tests cover valid, malformed, stale, missing, and out-of-range commands; accepted commands map to the declared setpoint units and active mode; invalid input follows the configured behavior and cannot bypass limits.

### SF-012 - Estimate attitude and angular rates

- **Size:** L
- **Requirements:** FCS-F-014, FCS-F-020, FCS-F-021, FCS-F-024
- **Depends on:** SF-005, SF-006; Decision: estimator algorithm, sensor alignment, latency/validity limits, and supported IMU configuration.
- **Story:** As a controller, I need validated attitude and angular-rate estimates with status so stabilization can use current state or detect when it cannot.
- **Acceptance checks:** Deterministic unit/SIL vectors verify output, units, and validity; invalid/stale inputs produce invalid estimates rather than plausible stale outputs; latency is measured against its configured budget; configured estimator validity limits are exercised.
- **Subtasks:** Implement estimator interface and deterministic core; integrate validated IMU inputs and validity outputs; verify reference vectors, invalid inputs, and latency.

### SF-013 - Bound and rate-limit control setpoints

- **Size:** M
- **Requirements:** FCS-F-032, FCS-F-033, FCS-F-039, FCS-S-006
- **Depends on:** SF-003, SF-011; Decision: aircraft operational limits and transition-rate limits.
- **Story:** As the controller, I need bounded and transition-limited setpoints so pilot or mission inputs cannot demand operation outside the configured envelope.
- **Acceptance checks:** Boundary tests verify values at, below, and above each configured limit; abrupt transitions are limited to configured rates; invalid limits prevent activation; output is deterministic and reports limiting/saturation status.

### SF-014 - Convert control demands to bounded motor outputs

- **Size:** L
- **Requirements:** FCS-F-034, FCS-F-035, FCS-F-037, FCS-S-005, FCS-S-006
- **Depends on:** SF-001, SF-003, SF-008, SF-013; Decision: airframe geometry, motor order/direction, mixer configuration, ESC command range and disarmed value.
- **Story:** As the FCS, I need to allocate control demands to configured motors and constrain commands to the ESC interface so output remains bounded and testable.
- **Acceptance checks:** Unit tests verify mixer outputs for declared airframe cases; all outputs remain within configured ESC bounds; invalid geometry/configuration is rejected; saturation is reported when allocation cannot meet demand; a single invalid input cannot produce unbounded output.
- **Subtasks:** Implement validated airframe allocation; implement output limiting and saturation reporting; test mixer vectors, invalid configuration, bounds, and disarmed behavior.

### SF-015 - Stabilize angular rate with anti-windup

- **Size:** M
- **Requirements:** FCS-F-030, FCS-F-036
- **Depends on:** SF-003, SF-012, SF-013, SF-014; Decision: controller gains, loop rate, and tracking/performance acceptance limits.
- **Story:** As the stabilized mode, I need rate feedback control with integral protection so rate demands are tracked without uncontrolled integral growth during saturation.
- **Acceptance checks:** Unit/SIL tests verify direction and response for bounded test vectors; saturation tests verify anti-windup behavior; invalid state or setpoint does not produce an unrestricted output; performance is compared with project-defined criteria.

### SF-016 - Control aircraft attitude in stabilized mode

- **Size:** M
- **Requirements:** FCS-F-031
- **Depends on:** SF-012, SF-013, SF-015; Decision: attitude-control design and tracking criteria.
- **Story:** As a stabilized-mode pilot, I need attitude commands converted into rate demands so the aircraft follows bounded attitude setpoints.
- **Acceptance checks:** SIL scenarios verify attitude error drives the declared rate-demand direction; configured limits are respected; invalid attitude estimate inhibits the attitude loop or selects its approved degraded behavior; acceptance uses project-defined tracking limits.

### SF-017 - Execute deterministic control cycles

- **Size:** M
- **Requirements:** FCS-NF-001, FCS-NF-002, FCS-NF-003, FCS-NF-008, FCS-NF-014
- **Depends on:** SF-005, SF-012, SF-014; SF-010; Decision: scheduler, cycle rate, end-to-end latency budget, and worst-case supported load.
- **Story:** As a maintainer, I need the control path to execute within defined timing under supported load so command-to-actuator behavior is measurable and repeatable.
- **Acceptance checks:** Instrumented SIL/target tests measure cycle frequency, worst-case execution time, and end-to-end latency; configured budgets are checked under representative maximum load; telemetry/logging load cannot starve the control path; timing violations surface to SF-010.

### SF-018 - Implement manual/stabilized mode transitions

- **Size:** M
- **Requirements:** FCS-F-020, FCS-F-052; section 5 mode-state requirements
- **Depends on:** SF-007, SF-011, SF-012, SF-015, SF-016; Decision: enabled modes, entry/exit conditions, and transition priorities.
- **Story:** As a pilot, I need explicit manual/stabilized mode transitions so only supported modes run with their required valid inputs.
- **Acceptance checks:** State-machine tests cover allowed, prohibited, and repeated transitions; entry requirements are enforced; invalid required state prevents or exits the mode according to configured policy; active mode and transition reason are observable.

### SF-019 - Apply fault-driven degraded or failsafe response

- **Size:** L
- **Requirements:** FCS-F-025, FCS-F-076, FCS-F-079, FCS-S-003, FCS-S-005, FCS-S-008, FCS-S-010, FCS-S-014
- **Depends on:** SF-006, SF-009, SF-010, SF-012, SF-018; Decision: aircraft-approved response per fault and recovery conditions.
- **Story:** As the FCS, I need invalid flight-critical state to select the approved degraded/failsafe behavior so control does not continue as if required estimates were valid.
- **Acceptance checks:** Fault injection verifies detection-to-response for each configured critical input; response is the one approved for that aircraft and does not depend on unavailable navigation; active safety mode and trigger are reported; critical faults do not automatically recover without defined conditions.
- **Subtasks:** Connect estimator validity to fault classification; implement response selection and safety-mode status; test sensor loss, recovery criteria, and competing faults.

## P2: Optional flight functions and system integration

### SF-020 - Estimate configured altitude and navigation state

- **Size:** L
- **Requirements:** FCS-F-015, FCS-F-016, FCS-F-017, FCS-F-018, FCS-F-022, FCS-F-023
- **Depends on:** SF-006, SF-012; Decision: installed barometer/GNSS/other sensors, fusion policy, validity criteria, and supported modes.
- **Story:** As an optional flight mode, I need estimates and validity status only from configured, valid sources so navigation functions can gate their use.
- **Acceptance checks:** Tests separately cover each installed source and absent-source configuration; altitude and navigation output include validity/confidence; invalid inputs cannot be represented as valid position/altitude; magnetometer measurements are validated before heading use; source availability is exposed per mode.
- **Subtasks:** Implement altitude estimate path for configured source; implement GNSS validity and navigation output path when equipped; validate magnetometer data before heading use when equipped; test source absence, invalidity, and output status.

### SF-021 - Gate and regulate Altitude Hold

- **Size:** M
- **Requirements:** FCS-F-040, FCS-F-041
- **Depends on:** SF-018, SF-020; Decision: supported altitude source, control design, limits, and performance criteria.
- **Story:** As a pilot, I need Altitude Hold enabled only with a valid altitude estimate so the mode cannot act on unavailable data.
- **Acceptance checks:** Mode-entry tests reject missing/invalid altitude; SIL tests verify bounded altitude regulation for valid input; loss of validity invokes the approved transition; numerical acceptance uses project-defined limits.

### SF-022 - Gate and regulate Position Hold

- **Size:** M
- **Requirements:** FCS-F-042, FCS-F-043, FCS-F-045
- **Depends on:** SF-018, SF-020, SF-019; Decision: supported navigation sources, control design, degradation response, and performance criteria.
- **Story:** As a pilot, I need Position Hold to require valid position and velocity estimates and respond explicitly to navigation degradation.
- **Acceptance checks:** Entry is rejected for invalid required estimates; SIL tests verify bounded response with valid estimates; injected temporary and sustained navigation loss follow distinct configured behavior; invalid navigation is never silently reused as valid.

### SF-023 - Enforce enabled flight-envelope constraints

- **Size:** M
- **Requirements:** FCS-F-044
- **Depends on:** SF-003, SF-013, SF-020; Decision: supported geofence, altitude, and speed limits and source validity requirements.
- **Story:** As the FCS, I need enabled altitude, speed, and geofence constraints enforced so supported modes remain within aircraft-configured limits.
- **Acceptance checks:** Boundary and exceedance tests cover each enabled constraint; unavailable or invalid data does not silently pass a constraint; disabled/not-installed functions are reported as unsupported rather than treated as satisfied.

### SF-024 - Validate autonomous mission input

- **Size:** M
- **Requirements:** FCS-F-053, FCS-F-055
- **Depends on:** SF-003, SF-023; Decision: mission schema, aircraft capability map, and operational constraints.
- **Story:** As an operator, I need missions rejected before acceptance if malformed, unsupported, or outside configured constraints.
- **Acceptance checks:** Tests cover valid mission, malformed data, unsupported command, and each configured constraint violation; rejection identifies the reason; acceptance does not start execution or arm motors by itself.

### SF-025 - Execute, pause, abort, and report mission progress

- **Size:** L
- **Requirements:** FCS-F-054, FCS-F-056
- **Depends on:** SF-018, SF-019, SF-023, SF-024; Decision: supported mission commands and approved pause/abort behavior.
- **Story:** As an operator, I need an accepted mission to execute in order and be pausable or abortable so mission behavior remains observable and controllable.
- **Acceptance checks:** SIL tests verify command order and progress; pause/abort are tested at each supported mission state; invalid prerequisites and safety events take precedence; mission state and termination reason are reported.
- **Subtasks:** Implement mission state and sequencing; implement pause/abort transitions; test progress, invalid prerequisites, and safety preemption.

### SF-026 - Implement controlled takeoff and landing behavior

- **Size:** L
- **Requirements:** FCS-F-064, FCS-F-065, FCS-F-066, FCS-F-067
- **Depends on:** SF-007, SF-014, SF-018, SF-019; Decision: supported takeoff/landing sensors, touchdown criteria, motor-output sequence, and approved in-flight disarm policy.
- **Story:** As a pilot, I need supported takeoff and landing functions to follow defined state transitions and motor-output behavior without unintended in-flight disarm.
- **Acceptance checks:** SIL tests cover takeoff, descent, touchdown, disarm, invalid input, and interrupted landing; output behavior matches the approved sequence; automatic in-flight disarm is prohibited unless explicitly approved; ground/bench output checks use propellers removed.
- **Subtasks:** Define and implement takeoff state path; define and implement landing/touchdown/disarm path; test nominal and interrupted flows.

### SF-027 - Monitor command-link loss and apply approved response

- **Size:** M
- **Requirements:** FCS-F-070, FCS-F-074, FCS-S-002, FCS-S-003, FCS-T-004
- **Depends on:** SF-009, SF-011, SF-019; Decision: command timeout/detection budget and aircraft-approved response.
- **Story:** As the FCS, I need to detect loss or invalidity of pilot input within its budget and apply the approved response.
- **Acceptance checks:** SIL/fault-injection tests cover disconnect, timeout, invalid data, and recovery; detection time is measured against the configured limit; selected action and reason match the approved policy; telemetry loss alone does not falsely indicate pilot-command loss.

### SF-028 - Monitor battery state and critical thresholds

- **Size:** M
- **Requirements:** FCS-F-071, FCS-F-075, FCS-T-006, FCS-T-007
- **Depends on:** SF-001, SF-009, SF-019; Decision: battery interface, measurement-validity rules, warning/critical thresholds, and approved responses.
- **Story:** As the FCS, I need to distinguish valid battery warnings from critical conditions and apply the approved response at each threshold.
- **Acceptance checks:** Tests cover below/at/above thresholds and implausible or missing measurements; warning and critical events are distinct and reported; critical response is selected from the approved fault policy; thresholds are configuration-driven and invalid values are rejected.

### SF-029 - Execute Return to Launch only with valid prerequisites

- **Size:** L
- **Requirements:** FCS-F-090, FCS-F-091, FCS-F-092, FCS-F-093
- **Depends on:** SF-018, SF-019, SF-020, SF-023; Decision: RTL support, home-position definition, route/altitude/termination, and navigation-loss response.
- **Story:** As a pilot, I need RTL to verify its prerequisites and follow the configured route so it cannot depend on unavailable navigation.
- **Acceptance checks:** Tests reject or choose the approved alternate when home position/navigation are invalid; SIL verifies configured route, altitude, and termination; mid-route navigation loss triggers the defined response; disabled RTL is reported unsupported and cannot be invoked.
- **Subtasks:** Implement prerequisite gate; implement configured RTL state/route; test initiation, termination, and navigation-loss cases.

### SF-030 - Implement hazard-approved emergency behavior

- **Size:** M
- **Requirements:** FCS-F-094; FCS-S-003, FCS-S-008, FCS-S-011
- **Depends on:** SF-009, SF-010, SF-019; Decision: completed aircraft-specific hazard analysis and approved emergency behavior for relevant power/software faults.
- **Story:** As the FCS, I need emergency behavior selected from the aircraft safety assessment so a generic motor-stop response is never assumed to be safe.
- **Acceptance checks:** Each implemented emergency trigger maps to an approved response and rationale; tests verify trigger, priority, and reported active state; no emergency behavior is enabled without an approved configuration; brownout/power-loss cases are covered to the extent supported by hardware.

### SF-031 - Report health and reject malformed communications

- **Size:** M
- **Requirements:** FCS-F-077, FCS-F-100, FCS-F-101, FCS-F-104, FCS-F-105, FCS-F-106, FCS-NF-015, FCS-T-005
- **Depends on:** SF-001, SF-006, SF-007, SF-009; Decision: telemetry protocol, supported fields, update rates, and communication error reporting.
- **Story:** As a pilot, I need concise health, mode, arming, sensor, battery, and failsafe status while malformed or unsupported messages are rejected.
- **Acceptance checks:** Protocol tests cover valid, malformed, unsupported, and interface-error messages; supported health fields reflect current internal state; telemetry loss while command input remains valid does not alter control behavior; reporting cannot expose an unsafe control interface or starve control timing.

### SF-032 - Record timestamped flight and fault events

- **Size:** M
- **Requirements:** FCS-F-078, FCS-F-102, FCS-F-103, FCS-NF-014, FCS-NF-015
- **Depends on:** SF-001, SF-009, SF-017; Decision: available storage, retention policy, event schema, and timing budget.
- **Story:** As a maintainer, I need ordered flight-critical and fault events retained where storage permits so post-flight investigation has useful evidence.
- **Acceptance checks:** Tests verify event ordering/timestamps, fault and mode content, storage-full behavior, and persistence across normal power cycles where non-volatile storage exists; logging load is bounded and cannot starve control; sensitive or unsafe control inputs are not exposed.

### SF-033 - Integrate simultaneous and cascading fault scenarios

- **Size:** M
- **Requirements:** FCS-F-080, FCS-S-009, FCS-S-013, FCS-T-012
- **Depends on:** SF-009, SF-019, SF-027, SF-028; SF-029 if RTL is enabled; Decision: approved fault combinations and expected arbitration outcomes.
- **Story:** As a safety tester, I need repeatable multi-fault scenarios so fault priority and cascading behavior can be verified as a system.
- **Acceptance checks:** Scenario tests inject the approved simultaneous/cascading fault combinations; each result matches the documented priority and active safety reason; unavailable navigation is not used by a navigation-dependent response; repeated runs produce the same selected behavior.

### SF-034 - Establish SIL fault-injection regression suite

- **Size:** L
- **Requirements:** FCS-T-001 through FCS-T-012; verification strategy section 11
- **Depends on:** SF-003, SF-006, SF-007, SF-009, SF-010, SF-014, SF-019, SF-027, SF-028, SF-033.
- **Story:** As a developer, I need automated SIL fault-injection coverage for baseline scenarios so safety and control regressions are detected on each change.
- **Acceptance checks:** Automated scenarios cover all FCS-T-001 through FCS-T-012 conditions applicable to implemented features; expected results are asserted, not just logged; random inputs use fixed seeds; the suite runs reproducibly and reports requirement/test IDs; unsupported hardware-only checks are identified rather than marked passed.
- **Subtasks:** Add deterministic vehicle/sensor test fixtures; implement baseline fault scenarios; connect scenario outcomes to requirement IDs and repeatable test execution.

### SF-035 - Verify target interfaces in HIL and propeller-off bench tests

- **Size:** L
- **Requirements:** FCS-F-002, FCS-F-003, FCS-F-013, FCS-F-035, FCS-NF-001 through FCS-NF-009; verification strategy section 11
- **Depends on:** SF-002, SF-004, SF-005, SF-010, SF-014, SF-017, SF-034; Decision: target hardware, HIL/bench setup, interface specifications, and approved test procedures.
- **Story:** As a verification engineer, I need target-level checks of timing, sensor/actuator interfaces, startup, and injected faults so SIL evidence is confirmed against the selected firmware platform.
- **Acceptance checks:** HIL/bench procedures identify configuration and software revision; sensor, actuator-interface, startup, timing, and supported fault injections have recorded pass/fail criteria; actuator checks are performed propeller-off under approved procedures; no uncontrolled flight test is part of this story.
- **Subtasks:** Define target test configuration and safe procedures; execute interface/startup/timing checks; execute applicable fault injections and retain traceable results.

## Dependency overview

The principal implementation path is:

`SF-001 -> SF-003/SF-004/SF-005 -> SF-006/SF-007/SF-009 -> SF-011/SF-012/SF-013 -> SF-014/SF-015/SF-016/SF-017/SF-018 -> SF-019`

Optional navigation and higher-level features branch from validated configuration and state:

`SF-006 -> SF-020 -> SF-021/SF-022/SF-023 -> SF-024 -> SF-025`

Safety response and verification converge here:

`SF-009/SF-019 -> SF-027/SF-028/SF-030/SF-033 -> SF-034 -> SF-035`

RTL is conditional and additionally depends on valid navigation and aircraft-approved route behavior (`SF-029`). Mission, altitude/position hold, RTL, and emergency behavior remain optional until their aircraft-specific decisions are approved.

## Requirement coverage notes

- Functional and safety requirements are linked on each story. Stories SF-001, SF-004, SF-010, SF-017, SF-031, SF-032, and SF-035 also cover cross-cutting non-functional requirements.
- Requirement IDs FCS-F-008, FCS-F-015/016, FCS-F-040 through FCS-F-045, FCS-F-053 through FCS-F-056, FCS-F-064 through FCS-F-067, FCS-F-090 through FCS-F-094, and FCS-F-103 are conditional on configured hardware/features or storage. The linked story acceptance checks must identify unsupported/not-installed cases explicitly.
- The backlog defines implementation and verification work, not aircraft safety approval, certification, or authorization to fly. Numeric acceptance criteria must be populated from the project-specific baseline before target acceptance.