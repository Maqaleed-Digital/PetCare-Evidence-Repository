# PETCARE DF18 — Execution Policy

## Sequencing
- follow DF17 ranking strictly
- do not skip higher priority items unless blocked

## Concurrency
- respect max_concurrent_executions
- enforce per_unit_execution_limit

## Deferral Logic
Items must be deferred if:
- capacity exceeded
- dependency unresolved
- conflict detected

## Conflict Definition
- same KPI impacted
- same unit overlapping
- shared dependency chain

## Scheduling Output
System must produce:
- execution_schedule.json
- deferred_queue.json
