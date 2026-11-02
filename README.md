# AI_L2_Training

Hardware-independent Python training baseline for the drone flight control
system. The current implementation provides validated configuration types,
sensor sample checks, startup/arming gates, explicit fault-policy arbitration,
bounded setpoints, and a configurable motor mixer with disarmed inhibition.

## Verify

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
```

The core and tests use only the Python 3.11+ standard library. The suite is
also compatible with pytest when it is available.

## Configuration boundary

Aircraft limits, sensor ranges and freshness budgets, mixer geometry, actuator
ranges, and approved fault responses are intentionally supplied by the project
configuration. No example aircraft values or generic failsafe actions are
provided. The modules do not access hardware and do not authorize motor testing
or flight.

The backlog stories that require selected hardware, calibrated estimator and
controller behavior, or approved aircraft safety decisions remain future work;
this package is a testable software foundation, not a complete flight stack.