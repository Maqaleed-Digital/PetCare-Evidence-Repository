# PETCARE DF17 — Portfolio Sequencing Policy

## Purpose
Control the order of execution across multiple units and optimization candidates.

## Sequencing Rules
- No conflicting optimizations may run in parallel
- Dependencies must resolve before downstream execution
- Higher-ranked items must be considered first
- Maximum concurrent execution count must be explicitly declared

## Conflict Examples
- Two optimizations changing the same KPI baseline
- Two optimizations targeting the same operating unit with overlapping operational windows
- A downstream item depending on an unexecuted upstream change

## Portfolio Guardrail
No unit may create local sequencing logic outside this policy.

## Required Sequence Output
- ranked_execution_queue.json
- blocked_items.json
- dependency_snapshot.json
