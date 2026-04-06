HOTFIX ACCEPTANCE

ACCESS
- landing page public
- sign-in page public
- onboarding page public
- unauthorized page renders as UI
- /app resolves by authenticated role
- owner/non-vet users do not hit raw forbidden JSON by default
- vet/admin protected routes remain enforced

UI
- landing page has improved hierarchy, spacing, and CTA structure
- dashboard shell uses polished cards, headers, empty states
- unauthorized page is branded and actionable
- loading state exists during session/role resolution

VALIDATION
- public route checks pass
- protected route checks pass
- unauthorized UX visible
- no raw forbidden JSON shown in normal browser journey
