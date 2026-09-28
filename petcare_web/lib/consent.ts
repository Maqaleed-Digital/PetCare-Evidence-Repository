/**
 * lib/consent.ts — pilot consent record (browser-local).
 *
 * MVC-UX-WO-002 WI-3. In the in-memory pilot we cannot persist a real
 * consent record (Cloud SQL is gated). To still display *something*
 * truthful in ConsentStateView, the register page writes a minimal
 * record to localStorage on successful registration:
 *   { consented_at: ISO, origin: 'pilot_invite' | 'self_registration', scope: string[] }
 *
 * X6 (MVC-EPC-D-001 D2): the record NEVER holds the invite code — a credential does not belong in browser storage.
 * Records written before D2 may carry `origin_invite_code`; it is ignored on read and dropped on the next write.
 *
 * Read-only consumer: ConsentStateView. Producer: app/register/page.tsx.
 *
 * When persistence comes online this module is replaced with a
 * server-side fetch; the component contract stays the same.
 */

export const CONSENT_KEY = 'vc_consent'

export interface ConsentRecord {
  consented_at: string             // ISO timestamp
  origin: 'pilot_invite' | 'self_registration'   // how the account was created — never the credential itself
  scope: readonly string[]         // scope identifiers — match STRINGS.consentState
}

export function readConsent(): ConsentRecord | null {
  if (typeof window === 'undefined') return null
  const raw = localStorage.getItem(CONSENT_KEY)
  if (!raw) return null
  try {
    const parsed = JSON.parse(raw)
    const { origin_invite_code: _legacy, ...rest } = parsed ?? {}
    return { origin: 'pilot_invite', ...rest } as ConsentRecord
  } catch {
    return null
  }
}

export function writeConsent(record: ConsentRecord): void {
  if (typeof window === 'undefined') return
  localStorage.setItem(CONSENT_KEY, JSON.stringify(record))
}
