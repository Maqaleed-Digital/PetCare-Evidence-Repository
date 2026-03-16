CONSENT GATE POLICY

Purpose:
Define where orchestration must check consent before advancing.

Consent-gated transitions:
- owner data read across domains
- referral packet release
- partner sharing flows
- any non-owner shared view

Rules:
- missing or revoked consent must block gated transition
- blocked state must return explicit reason code
