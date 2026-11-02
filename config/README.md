# Configuration Boundary

No aircraft configuration is baselined yet. Do not add assumed sensor ranges,
freshness budgets, command limits, motor order, mixer geometry, or actuator
inhibit values here.

The current in-process configuration contract is represented by `Bounds`,
`SensorRule`, `MixerConfig`, and `FcsConfig` in `src/fcs/config.py`. Populate
these from an approved aircraft configuration only after the external decisions
listed in `docs/software_firmware_stories.md` are resolved. Invalid or missing
configuration must prevent the dependent function from becoming usable.

Implemented foundation: SF-003 validation primitives, with unit coverage for
invalid numerical bounds and mixer shape. A persistent configuration format,
protected runtime parameter storage, and full schema diagnostics remain open.