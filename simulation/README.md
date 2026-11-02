# SIL Verification Boundary

`tests/test_fcs_core.py` currently provides deterministic, hardware-independent
contract checks for configuration bounds, sensor validity, arming gates,
fault-policy selection, pilot-command validation, bounded setpoints, and
disarmed motor inhibition. Test vectors are synthetic; their numerical values
are not aircraft limits.

Run the checks from the repository root using the command in `README.md`. These
checks do not simulate vehicle dynamics, hardware timing, sensor protocols, or
an approved aircraft failsafe response. HIL, bench, motor, and flight testing
are not implemented or authorized by this training baseline.

Partial story coverage: SF-003, SF-004, SF-006, SF-007, SF-008, SF-009,
SF-011, SF-013, and SF-014. These are software primitives, not completion of
the linked stories' full acceptance criteria. Other stories remain unimplemented
until their dependencies and project decisions are available.