DF40 Fairness Review and Appeal Model

Purpose

Define the minimum governance model for review, restriction, appeal, and restoration of fair commercial treatment.

Review Objects

1. fairness review record
Captures owner, domain, comparison class, rule basis, and review outcome

2. restriction proposal record
Captures proposed action, reason code, expected impact, and supporting evidence

3. approval record
Captures approver identity, approval reference, bounded limits, and timestamp

4. active control record
Captures active fairness control or restriction, validity window, and rollback posture

5. appeal record
Captures appellant, appeal grounds, reviewer, and disposition

6. restoration record
Captures end state, restored baseline, and linked evidence

Mandatory Fields

fairness_action_id
owner
enforcement_review_mode
market_abuse_ruleset_ref
partner_treatment_standard_ref
approval_id
affected_domain
comparison_class
reason_code
valid_from
valid_to
rollback_rule
appeal_path
audit_trace_id
status

Statuses

BLOCKED
CONTROLLED
ACTIVE_GOVERNED
UNDER_REVIEW
APPEALED
ROLLED_BACK
EXPIRED

Evidence Integrity

All evidence bundles must include:
1. deterministic file listing
2. git head
3. manifest json
4. manifest sha256

Review Cadence

1. activation review at launch
2. periodic fairness review during active window
3. appeal review when invoked
4. restoration review on expiry or rollback
