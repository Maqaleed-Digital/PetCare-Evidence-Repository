# PETCARE Production Infrastructure Activation Runbook

## Purpose

This runbook governs the activation stage after architecture and governance baseline completion.

## Activation Authority

Recommended executor:
- Claude Code for deterministic repo-native file generation

Equivalent executor:
- Terminal using the same canonical block

Final authority:
- operator validates environment facts outside source control
- pushed commit hash becomes source of truth

## Execution Steps

1. Confirm source-of-truth baseline commit
2. Confirm clean working tree
3. Generate activation plan, checklist, runbook, and execution script
4. Generate evidence file list and SHA-256 manifest
5. Commit
6. Push origin HEAD
7. Record pushed commit hash
8. Update Notion with evidence path and new source of truth

## Mandatory Non-Negotiables

- PetCare remains standalone
- AWS remains the cloud baseline for this blueprint
- AI remains assistive-only
- HITL remains hard-gated
- KSA-ready data posture remains preserved
- tenant isolation remains enforced
- DR objective remains documented
- evidence discipline remains deterministic

## Required Evidence Output

- ACTIVITY_LOG.txt
- FILE_LIST.txt
- SHA256SUMS.txt
- MANIFEST.json

## Failure Handling

If any step fails:
- do not patch around failure
- do not continue
- paste exact logs
- treat failure logs as stop condition evidence
