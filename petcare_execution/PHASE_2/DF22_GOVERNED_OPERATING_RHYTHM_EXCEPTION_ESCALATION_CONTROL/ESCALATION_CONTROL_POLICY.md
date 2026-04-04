# PETCARE DF22 — Escalation Control Policy

## Purpose
Define fail-closed escalation routing and approval rules.

## Escalation Triggers
- exception_class = HIGH
- exception_class = CRITICAL
- baseline deviation beyond approved tolerance
- governance checkpoint missed
- required owner unavailable

## Escalation Outputs
- escalation_record.json
- escalation_route.txt
- decision_log.txt

## Rules
- HIGH exceptions require escalation
- CRITICAL exceptions require immediate escalation
- no closure of escalated exception without recorded review
- escalation route must be explicit and auditable

## Forbidden
- bypassing escalation
- suppressing critical escalation
- closing escalated exception without review evidence
