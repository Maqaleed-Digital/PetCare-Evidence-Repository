# PetCare Evidence Analysis — Sprint 6 PRD

## Project Overview
- **Project Name:** PetCare Evidence Analysis — Sprint 6
- **Project Type:** Evidence Analysis + UI Dashboard
- **Repository:** https://github.com/Waheebow/PetCare-Evidence-Repository
- **Analysis Date:** 2026-01-23

## Original Problem Statement
1. Perform standalone evidence analysis for PetCare KSA platform covering A-E sections
2. Build a PetCare UI-0 scaffold (React + Tailwind) with governance dashboard

## User Personas
- **Board/Regulator:** Requires audit-ready documentation
- **Security Team:** Needs RBAC and RLS validation
- **Ops Leadership:** Requires stability assessment
- **Governance Team:** Needs AI explainability review

## Core Requirements (Static)
- [x] Clone/load evidence repository
- [x] Validate SHA256 checksums
- [x] Produce structured A-E analysis report
- [x] Identify UI-0 readiness signals
- [x] Build React UI with left navigation
- [x] Evidence Packs browser with file verification
- [x] Governance Summary (A-E cards)
- [x] Security Review (RLS status, bypass roles)
- [x] Audit Event Explorer with filters
- [x] Explainability Explorer (rule runs + logs)
- [x] Markdown Report Viewer

## What's Been Implemented
| Date | Task | Status |
|------|------|--------|
| 2026-01-23 | Repository cloning | ✅ Complete |
| 2026-01-23 | Integrity verification (49/50 files) | ✅ Complete |
| 2026-01-23 | A-E Analysis Report | ✅ Complete |
| 2026-01-23 | Backend API (14 endpoints) | ✅ Complete |
| 2026-01-23 | Dashboard page | ✅ Complete |
| 2026-01-23 | Evidence Packs page | ✅ Complete |
| 2026-01-23 | Evidence Pack Detail page | ✅ Complete |
| 2026-01-23 | Governance page | ✅ Complete |
| 2026-01-23 | Audit Events page | ✅ Complete |
| 2026-01-23 | Explainability page | ✅ Complete |
| 2026-01-23 | Security page | ✅ Complete |
| 2026-01-23 | Report Viewer page | ✅ Complete |
| 2026-01-23 | Evidence browser with manifest verification | ✅ Complete |
| 2026-01-23 | Addendum section for supplemental files | ✅ Complete |
| 2026-01-23 | ALL OK / PARTIAL manifest status display | ✅ Complete |
| 2026-01-23 | Testing (100% pass) | ✅ Complete |

## Architecture

### Frontend (React + Tailwind)
- `/dashboard` - Overview with metrics and A-E cards
- `/evidence` - Evidence packs list
- `/evidence/:packId` - File browser with SHA256 verification
- `/governance` - A-E section summaries
- `/audit` - Audit event explorer with filters
- `/explainability` - Rule runs and logs tabs
- `/security` - RLS status and bypass roles
- `/report` - Markdown report viewer

### Backend (FastAPI)
- `GET /api/evidence/packs` - List evidence packs
- `GET /api/evidence/packs/:pack/files` - List files with verification
- `GET /api/evidence/packs/:pack/file?path=` - Download file
- `GET /api/governance/summary` - A-E governance cards
- `GET /api/security/rls` - RLS status by table
- `GET /api/security/bypassrls` - Roles with bypass privilege
- `GET /api/security/policies` - RLS policies
- `GET /api/security/grants` - Role table grants
- `GET /api/audit/events` - Audit events with filters
- `GET /api/audit/event-types` - Available event types
- `GET /api/explainability/runs` - TCF rule runs
- `GET /api/explainability/logs` - Explainability logs
- `GET /api/report/day3` - Markdown report

## Key Findings Summary
- System state: IDLE/PRE-PILOT
- Activity: Manual insert proofs only
- Clinical signals: NONE
- AI Governance: GREEN
- Security posture: AMBER (RLS partial)

## Prioritized Backlog
### P0 (Blocking)
- None identified

### P1 (High Priority)
- [ ] Enable RLS on `app.audit_events`
- [ ] Verify `anon` role grants are intentional

### P2 (Medium Priority)
- [ ] Generate baseline workload for metrics
- [ ] Test HITL workflow paths
- [ ] Validate AI integration logging
- [ ] Add data visualization charts
- [ ] Export functionality for reports

## Next Phase: Sprint UI-1
- Add data visualization (Recharts)
- Real-time monitoring views
- Authentication layer
- Multi-pack support
