DF43 Approved Runtime Control Catalog

ARC-01
Name
Sensitive activation block control

Allowed When
Used to block governed actions until required approvals and references are present

Required Controls
approval reference
guardrail ruleset
owner
audit trace

ARC-02
Name
Boundary enforcement control

Allowed When
Used to block execution outside approved governance boundaries

Required Controls
boundary definition
runtime mode
evidence trace
operator visibility

ARC-03
Name
Critical degradation stop control

Allowed When
Used to block unsafe continuation after critical guardrail failure

Required Controls
failure signal
safe fallback definition
review owner
restoration posture

ARC-04
Name
Temporary disablement control

Allowed When
Used only for explicitly approved, time-bounded runtime maintenance or recovery scenarios

Required Controls
approval reference
duration
owner
restoration evidence

Universal Rule

No runtime control may silently degrade or permanently weaken the governance model.
