# PORTFOLIO_ADMISSION_AUTHORITY_MODEL

## Purpose
This document defines the authority model for admitting clinics into steady-state portfolio operation.

## Authority layers
The authority structure contains:

1. portfolio governance authority
2. clinic-wave review authority
3. local clinic operating authority

## Authority rules
- portfolio governance retains final admission authority
- clinic-wave review may recommend but not finalize admission
- local clinic ownership may not self-admit
- remediation closure affecting admission remains portfolio-governed

## Decision boundaries
Only portfolio governance may authorize:

- steady-state admission
- return to remediation after failed exit review
- post-admission reclassification due to control drift
