'use client'

/**
 * AuditTrailLink — WI-8 DARK SCAFFOLD (Register F-01).
 *
 * Renders a link to the originating audit event ONLY when:
 *   1. FEATURE_AI is ON (AI/agent outputs need this surface), AND
 *   2. A real audit event handle is supplied (i.e., persistence has
 *      produced one — none exists in the in-memory pilot).
 *
 * In the pilot both gates are typically false → component returns null.
 */

import { FEATURE_AI, type AuditEventHandle } from '@/lib/featureFlags'
import { useLang } from '@/components/LangProvider'
import { STRINGS } from '@/lib/strings'

interface Props {
  eventHandle: AuditEventHandle
}

export function AuditTrailLink({ eventHandle }: Props) {
  if (!FEATURE_AI) return null
  if (!eventHandle) return null

  const { t } = useLang()
  const s = STRINGS.auditTrail

  return (
    <a
      href={`/audit/${encodeURIComponent(eventHandle.audit_event_id)}`}
      data-testid="audit-trail-link"
      style={{
        fontSize: 12, color: 'var(--accent)', textDecoration: 'underline',
      }}
    >
      {t(s.linkLabel)} →
    </a>
  )
}
