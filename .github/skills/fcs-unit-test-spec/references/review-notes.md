# Review Notes

## Status Selection

- `PROPOSED`: the unit boundary and symbolic oracle are clear enough to propose, but this does not mean implemented or executed.
- `BLOCKED`: a missing external decision or source contract prevents a defensible oracle.
- `CONDITIONAL`: the case is meaningful only for an explicitly enabled/configured feature or after named evidence is approved.
- `NOT_APPLICABLE`: the behavior is outside the selected configuration/scope; state the reason.

Do not mark a case automation-ready merely because it can be expressed with a fake. Required thresholds, protocol semantics, fault tables, timing budgets, and response policies must come from approved source criteria.

## Unit Boundary

A case should exercise one unit's public/observable contract. Local dependency injection, deterministic clocks, and fakes/stubs are acceptable. A test that needs interactions among multiple logical modules or target behavior belongs in a gap or `OUT_OF_SCOPE` record, not a unit case.

## Validator Limits

`scripts/validate_spec.py` verifies CSV structure, required case fields/statuses, unique IDs, story coverage, and that referenced requirement identifiers appear in the SRS. It cannot determine whether a source interpretation is correct, whether an oracle is safe, or whether software passes. Human review against the normative documents remains required.