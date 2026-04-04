# PETCARE DF17 — Scoring Model Governance

## Model Type
Hybrid governed override architecture

## Default Locked Weights
- KPI_IMPACT_WEIGHT = 0.40
- RISK_WEIGHT = 0.30
- EFFORT_WEIGHT = 0.20
- URGENCY_WEIGHT = 0.10

## Score Formula
PRIORITY_SCORE =
(KPI_IMPACT_WEIGHT * expected_improvement)
+
(RISK_WEIGHT * inverse_risk)
+
(EFFORT_WEIGHT * inverse_effort)
+
(URGENCY_WEIGHT * urgency)

## Determinism Requirements
- Same inputs must always produce same output
- No dynamic learning
- No hidden coefficients
- No runtime mutation of defaults

## Explainability Requirement
The system must always be able to show:
- weights_version
- weights_used
- score_inputs
- score_output
- override_reference if applicable

## Rank Ordering
Higher PRIORITY_SCORE ranks first.

## Tie Break Order
1. lower risk
2. higher urgency
3. lower effort
4. lexical backlog item id
