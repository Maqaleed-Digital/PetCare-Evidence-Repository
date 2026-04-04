DF43 Prohibited Runtime Bypass Patterns

PRB-01
Silent approval bypass
Execution of governed actions without required approval evidence

PRB-02
Hidden control disablement
Any runtime weakening or disablement of guardrails without visible accountable record

PRB-03
Unsafe continuation
Continuation after critical guardrail failure without approved safe fallback

PRB-04
Boundary drift execution
Operation outside approved governance boundaries without controlled block

PRB-05
Invisible degraded mode
Any degraded runtime state not surfaced to operators and evidence logs

Blocking Rule

If any prohibited runtime bypass pattern is detected, activation must fail closed pending human review.
