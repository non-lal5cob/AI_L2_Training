# CSV Contract

The specification is a UTF-8 CSV with exactly this header and order:

```text
record_type,record_id,unit_or_behavior,story_ids,requirement_ids,dependencies,applicability,setup_preconditions,inputs_or_injected_condition,expected_observable_result,status,blocking_decision_or_evidence,fixture_or_test_seam,verification_scope,notes
```

Use comma delimiters and standard CSV quoting: quote fields containing commas, quotes, or line breaks and double embedded quotes. Keep each data record on one physical line. Leave inapplicable fields empty rather than changing the schema.

Allowed `record_type` values are `CONTEXT`, `PRINCIPLE`, `FIXTURE`, `CASE`, `GAP`, and `OUT_OF_SCOPE`. Assign stable unique IDs to every record; case IDs use the `UT-001` style. Put scope caveats in `CONTEXT`, design rules in `PRINCIPLE`, local seams in `FIXTURE`, test proposals in `CASE`, underspecified/uncovered behavior in `GAP`, and integration/SIL/HIL/bench/target evidence in `OUT_OF_SCOPE`.

Every case includes story and requirement IDs, dependencies, applicability, setup, injected input, an explicit observable result, status, and any decision/evidence that blocks or conditions it. Use only these case statuses: `PROPOSED`, `BLOCKED`, `CONDITIONAL`, and `NOT_APPLICABLE`. A `PROPOSED` case remains a proposal, not evidence that software behavior was executed.

Represent every story SF-001 through SF-035 in one or more `CASE`, `GAP`, or `OUT_OF_SCOPE` records. Cross-reference requirement IDs to the SRS. The context must say the file reviews specification completeness and traceability only; it does not demonstrate software behavior, aircraft safety, performance, hardware compatibility, or operational readiness.