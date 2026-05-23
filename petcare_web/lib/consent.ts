/**
 * lib/consent.ts — pilot consent record (browser-local).
 *
 * MVC-UX-WO-002 WI-3. In the in-memory pilot we cannot persist a real
 * consent record (Cloud SQL is gated). To still display *something*
 * truthful in ConsentStateView, the register page writes a minimal
 * record to localStorage on successful registration:
 *   { consented_at: ISO, origin_invite_code: string, scope: string[] }
 *
 * Read-only consumer: ConsentStateView. Producer: app/register/page.tsx.
 *
 * When persistence comes online this module is replaced with a
 * server-side fetch; the component contract stays the same.
 */

export const CONSENT_KEY = 'vc_consent'

export interface ConsentRecord {
  consented_at: string             // ISO timestamp
  origin_invite_code: string       // pilot invite code that authorised
  scope: readonly string[]         // scope identifiers — match STRINGS.consentState
}

export function readConsent(): ConsentRecord | null {
  if (typeof window === 'undefined') return null
  const raw = localStorage.getItem(CONSENT_KEY)
  if (!raw) return null
  try {
    return JSON.parse(raw) as ConsentRecord
  } catch {
    return null
  }
}

export function writeConsent(record: ConsentRecord): void {
  if (typeof window === 'undefined') return
  localStorage.setItem(CONSENT_KEY, JSON.stringify(record))
}
