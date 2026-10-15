import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { LangProvider } from '@/components/LangProvider'
import VetProfilePage from '@/app/vet/profile/page'

/**
 * J-V1 internal portion — CV-12 licence status (MVC-EPC-D-001 D3a, R21.4; R19.3). The page reports the licence and authority as
 * the server holds them, distinguishes a staff ATTESTATION from an authority lookup, always states that registry verification is
 * not available (X-33), and never claims an authority is in force when the server cannot say so (no tenant yet: fail closed).
 */
function res(body: unknown, status = 200) {
  return Promise.resolve({ ok: status >= 200 && status < 300, status, json: () => Promise.resolve(body) } as Response)
}
const LIC = { licence_id: 'l-1', licence_number: 'LIC-1', issuing_authority: 'MEWA', expires_on: '2031-12-31',
  submitted_at: '2031-01-01T06:00:00+00:00', status: 'SUBMITTED', verification: null }
const route = (licences: unknown, authority: unknown, authorityStatus = 200) => (u: string) =>
  String(u).endsWith('/me/licence') ? res(licences) : res(authority, authorityStatus)

beforeEach(() => { vi.restoreAllMocks(); localStorage.clear() })

describe('J-V1 internal — veterinarian licence status', () => {
  it('a submitted licence with no tenant yet: not in force (fail closed), registry notice, no untranslated copy', async () => {
    vi.stubGlobal('fetch', vi.fn(route([LIC], { detail: 'no tenant' }, 403)))
    render(<LangProvider><VetProfilePage /></LangProvider>)
    await waitFor(() => expect(screen.getByTestId('vet-licence')).toBeTruthy())
    expect(screen.getByTestId('vet-licence').getAttribute('data-status')).toBe('SUBMITTED')
    expect(screen.getByTestId('vet-authority').getAttribute('data-in-force')).toBe('false')
    expect(screen.getByTestId('vet-registry-notice').textContent).toMatch(/السجل الرسمي/)
    const main = document.querySelector('main') as HTMLElement
    const copy = main.cloneNode(true) as HTMLElement
    copy.querySelectorAll('[translate="no"]').forEach(n => n.remove())
    expect(copy.textContent).not.toMatch(/[A-Za-z]/)
  })

  it('a staff-verified licence reads as an attestation, never as a registry check, with the authority in force', async () => {
    const verified = { ...LIC, status: 'VERIFIED', verification: { method: 'MANUAL_STAFF', verified_at: '2031-01-02T06:00:00+00:00' } }
    vi.stubGlobal('fetch', vi.fn(route([verified], { in_force: true, reason: null, grants: [{ expires_at: '2031-12-31T21:00:00+00:00' }] })))
    localStorage.setItem('vc_lang', 'en')
    render(<LangProvider><VetProfilePage /></LangProvider>)
    await waitFor(() => expect(screen.getByTestId('vet-authority').getAttribute('data-in-force')).toBe('true'))
    expect(screen.getByTestId('vet-licence-status').textContent).toBe('Verified by a named staff member (recorded attestation)')
    expect(screen.getByTestId('vet-licence-status').textContent).not.toMatch(/registry|lookup/i)
    expect(screen.getByTestId('vet-registry-notice').textContent).toMatch(/not a registry check/)
  })

  it('an authority lookup is named as such', async () => {
    const looked = { ...LIC, status: 'VERIFIED', verification: { method: 'AUTHORITY_LOOKUP', verified_at: '2031-01-02T06:00:00+00:00' } }
    vi.stubGlobal('fetch', vi.fn(route([looked], { in_force: true, reason: null, grants: [] })))
    localStorage.setItem('vc_lang', 'en')
    render(<LangProvider><VetProfilePage /></LangProvider>)
    await waitFor(() => expect(screen.getByTestId('vet-licence-status').textContent).toBe('Verified by an issuing-authority lookup'))
  })
})
