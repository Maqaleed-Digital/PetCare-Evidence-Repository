import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { LangProvider } from '@/components/LangProvider'
import VetPrescriptionsPage from '@/app/vet/prescriptions/page'
import PharmacyPage from '@/app/pharmacy/page'
import SecurityPage from '@/app/account/security/page'
import contract from './fixtures/epc-b-server-contract.json'

/**
 * MVC-EXTERNAL-PRODUCTION-CLOSURE-001 Lane B (MVC-EPC-B-001) — the web client consumes the served step-up contract.
 *
 * FINDING NO_E2E_HARNESS: the repository's Playwright suite mocks the backend at the network layer; there is no harness
 * that drives the web client against a running petcare_api. These tests therefore answer with the server's OWN
 * responses, recorded from main:app at the Lane B baseline (fixtures/epc-b-server-contract.json — secrets synthetic).
 */

type Name = keyof typeof contract.responses
const served = (name: Name) => {
  const r = contract.responses[name]
  return Promise.resolve(new Response(JSON.stringify(r.body), { status: r.status, headers: { 'Content-Type': 'application/json' } }))
}
const ok = (body: unknown) => Promise.resolve(new Response(JSON.stringify(body), { status: 200, headers: { 'Content-Type': 'application/json' } }))
const CODE = '246810'
const RECOVERY = 'TEST-CODE-0001-XXXX'

type Call = { method: string; url: string; body: string }
let calls: Call[]
function stub(route: (c: Call, n: number) => Promise<Response> | undefined) {
  calls = []
  vi.stubGlobal('fetch', vi.fn((url: string, init?: RequestInit) => {
    const c = { method: init?.method ?? 'GET', url: String(url), body: typeof init?.body === 'string' ? init.body : '' }
    calls.push(c)
    const n = calls.filter(x => x.method === c.method && x.url === c.url).length
    return route(c, n) ?? ok([])
  }))
}
const count = (method: string, suffix: string) => calls.filter(c => c.method === method && c.url.endsWith(suffix)).length

const vetDefaults = (c: Call) => {
  if (c.url.endsWith('/api/practitioners/me/authority')) return ok({ in_force: true, reason: null })
  if (c.url.includes('/queue/')) return ok([])
  return undefined
}

async function issuePrescription(user: ReturnType<typeof userEvent.setup>) {
  await waitFor(() => expect(screen.getByTestId('issue-button')).not.toBeDisabled())
  for (const name of ['pet_id', 'session_id', 'medication_name', 'dosage', 'instructions'])
    await user.type(document.querySelector(`input[name="${name}"]`) as HTMLInputElement, 'x')
  await user.click(screen.getByTestId('issue-button'))
}

beforeEach(() => { vi.restoreAllMocks(); localStorage.clear(); sessionStorage.clear() })
afterEach(() => { vi.unstubAllGlobals() })

describe('Lane B — web step-up UX against the served contract', () => {
  it('a step-up refusal opens the prompt; after success the ORIGINAL request is retried once and its result shown', async () => {
    stub((c, n) => {
      if (c.method === 'POST' && c.url.endsWith('/api/prescriptions')) return n === 1 ? served('prescribe_without_step_up') : ok({ prescription_id: 'rx-9' })
      if (c.url.endsWith('/api/me/mfa/step-up')) return served('step_up_success')
      return vetDefaults(c)
    })
    render(<LangProvider><VetPrescriptionsPage /></LangProvider>)
    const user = userEvent.setup()
    await issuePrescription(user)
    const dialog = await screen.findByRole('dialog')
    expect(document.activeElement).toBe(within(dialog).getByLabelText('رمز التحقق'))      // focus moved into the prompt
    await user.type(within(dialog).getByLabelText('رمز التحقق'), CODE)
    await user.click(within(dialog).getByRole('button', { name: 'تحقق' }))
    await waitFor(() => expect(screen.queryByRole('dialog')).toBeNull())
    await waitFor(() => expect(count('POST', '/api/prescriptions')).toBe(2))
    const [first, retry] = calls.filter(c => c.method === 'POST' && c.url.endsWith('/api/prescriptions'))
    expect(retry.body).toBe(first.body)                                                  // the ORIGINAL request, unchanged
    expect(JSON.parse(calls.find(c => c.url.endsWith('/api/me/mfa/step-up'))!.body)).toEqual({ code: CODE })
    await waitFor(() => expect(count('GET', '/queue/awaiting-verification')).toBeGreaterThanOrEqual(2))  // retry result used
    expect(screen.queryByRole('alert')).toBeNull()
  })

  it('a second step-up refusal is shown as an error — no second prompt, no loop', async () => {
    stub(c => {
      if (c.method === 'POST' && c.url.endsWith('/api/prescriptions')) return served('prescribe_without_step_up')
      if (c.url.endsWith('/api/me/mfa/step-up')) return served('step_up_success')
      return vetDefaults(c)
    })
    render(<LangProvider><VetPrescriptionsPage /></LangProvider>)
    const user = userEvent.setup()
    await issuePrescription(user)
    const dialog = await screen.findByRole('dialog')
    await user.type(within(dialog).getByLabelText('رمز التحقق'), CODE)
    await user.click(within(dialog).getByRole('button', { name: 'تحقق' }))
    expect(await screen.findByTestId('step-up-still-required')).toBeInTheDocument()
    await new Promise(r => setTimeout(r, 50))
    expect(screen.queryByRole('dialog')).toBeNull()
    expect(count('POST', '/api/prescriptions')).toBe(2)
    expect(count('POST', '/api/me/mfa/step-up')).toBe(1)
  })

  it('an always-fresh operation prompts on EVERY attempt — the client never remembers a step-up', async () => {
    stub((c, n) => {
      if (c.url.endsWith('/api/me/mfa/enrol')) return n % 2 === 1 ? served('replace_factor_without_step_up') : served('enrol_success')
      if (c.url.endsWith('/api/me/mfa/step-up')) return served('step_up_success')
      return undefined
    })
    const { unmount } = render(<LangProvider><SecurityPage /></LangProvider>)
    const user = userEvent.setup()
    for (const attempt of [1, 2]) {                                           // seconds apart: well inside 15 minutes
      if (attempt === 2) { unmount(); render(<LangProvider><SecurityPage /></LangProvider>) }
      await user.click(await screen.findByTestId('mfa-start'))
      const dialog = await screen.findByRole('dialog')
      await user.type(within(dialog).getByLabelText('رمز التحقق'), CODE)
      await user.click(within(dialog).getByRole('button', { name: 'تحقق' }))
      await screen.findByTestId('mfa-confirm')
    }
    expect(count('POST', '/api/me/mfa/enrol')).toBe(4)                         // each attempt asked the server first
    expect(count('POST', '/api/me/mfa/step-up')).toBe(2)                       // and prompted each time
  })

  it('a recovery code works once as the step-up and is not retained by the client', async () => {
    const log = vi.spyOn(console, 'log'), warn = vi.spyOn(console, 'warn'), err = vi.spyOn(console, 'error'), info = vi.spyOn(console, 'info')
    stub((c, n) => {
      if (c.method === 'POST' && c.url.endsWith('/api/prescriptions')) return n === 1 ? served('prescribe_without_step_up') : ok({ prescription_id: 'rx-9' })
      if (c.url.endsWith('/api/me/mfa/recovery')) return served('recovery_success')
      return vetDefaults(c)
    })
    render(<LangProvider><VetPrescriptionsPage /></LangProvider>)
    const user = userEvent.setup()
    await issuePrescription(user)
    const dialog = await screen.findByRole('dialog')
    await user.click(within(dialog).getByRole('button', { name: 'استخدام رمز استرداد بدلاً من ذلك' }))
    await user.type(within(dialog).getByLabelText('رمز الاسترداد'), RECOVERY)
    await user.click(within(dialog).getByRole('button', { name: 'تحقق' }))
    await waitFor(() => expect(count('POST', '/api/prescriptions')).toBe(2))
    expect(count('POST', '/api/me/mfa/recovery')).toBe(1)
    // nowhere but the one step-up request
    expect(calls.filter(c => c.body.includes(RECOVERY)).map(c => c.url.replace(/^.*\/api/, '/api'))).toEqual(['/api/me/mfa/recovery'])
    expect(document.body.innerHTML).not.toContain(RECOVERY)
    expect(JSON.stringify({ ...localStorage })).not.toContain(RECOVERY)
    expect(JSON.stringify({ ...sessionStorage })).not.toContain(RECOVERY)
    expect(document.cookie).not.toContain(RECOVERY)
    for (const spy of [log, warn, err, info]) expect(JSON.stringify(spy.mock.calls)).not.toContain(RECOVERY)
  })

  it('no TOTP code reaches storage, the console or any request other than the step-up', async () => {
    const spies = ['log', 'warn', 'error', 'info', 'debug'].map(m => vi.spyOn(console, m as 'log'))
    const setItem = vi.spyOn(Storage.prototype, 'setItem')
    stub((c, n) => {
      if (c.method === 'POST' && c.url.endsWith('/api/prescriptions')) return n === 1 ? served('prescribe_without_step_up') : ok({})
      if (c.url.endsWith('/api/me/mfa/step-up')) return n === 1 ? served('step_up_wrong_code') : served('step_up_success')
      return vetDefaults(c)
    })
    render(<LangProvider><VetPrescriptionsPage /></LangProvider>)
    const user = userEvent.setup()
    await issuePrescription(user)
    const dialog = await screen.findByRole('dialog')
    await user.type(within(dialog).getByLabelText('رمز التحقق'), '111111')
    await user.click(within(dialog).getByRole('button', { name: 'تحقق' }))
    expect(await within(dialog).findByRole('alert')).toHaveTextContent('الرمز غير صحيح')   // error announced
    expect((within(dialog).getByLabelText('رمز التحقق') as HTMLInputElement).value).toBe('')  // cleared after submit
    await user.type(within(dialog).getByLabelText('رمز التحقق'), CODE)
    await user.click(within(dialog).getByRole('button', { name: 'تحقق' }))
    await waitFor(() => expect(count('POST', '/api/prescriptions')).toBe(2))
    for (const code of ['111111', CODE]) {
      expect(calls.filter(c => c.body.includes(code)).every(c => c.url.endsWith('/api/me/mfa/step-up'))).toBe(true)
      expect(JSON.stringify(setItem.mock.calls)).not.toContain(code)
      expect(document.cookie).not.toContain(code)
      for (const spy of spies) expect(JSON.stringify(spy.mock.calls)).not.toContain(code)
    }
  })

  it('pending (re-)enrolment routes the user to enrolment — no prompt, no bypass', async () => {
    stub(c => {
      if (c.method === 'POST' && c.url.endsWith('/api/prescriptions')) return served('prescribe_without_factor')
      return vetDefaults(c)
    })
    render(<LangProvider><VetPrescriptionsPage /></LangProvider>)
    await issuePrescription(userEvent.setup())
    const notice = await screen.findByTestId('enrolment-required')
    expect(within(notice).getByRole('link')).toHaveAttribute('href', '/account/security')
    expect(screen.queryByRole('dialog')).toBeNull()
    expect(count('POST', '/api/prescriptions')).toBe(1)
  })

  it('dispensing (SQ-3 item 1) goes through the same step-up and retry', async () => {
    const RX = { prescription_id: 'rx-1', pet_id: 'p', medication_name: 'Amoxicillin', dosage: '50mg', instructions: 'x',
                 status: 'VET_VERIFIED', issued_at: null, verified_at: null, verified_by_vet_id: null, issuing_vet_id: 'v' }
    stub((c, n) => {
      if (c.url.includes('/queue/awaiting-dispense')) return ok(calls.some(x => x.url.endsWith('/dispense') && x.method === 'POST' && n > 1) ? [] : [RX])
      if (c.url.endsWith('/dispense')) return n === 1 ? Promise.resolve(new Response(JSON.stringify({ detail: {
        ...contract.responses.prescribe_without_step_up.body.detail, operation: 'POST /api/prescriptions/{prescription_id}/dispense' } }),
        { status: 403 })) : ok({ ...RX, status: 'DISPENSED' })
      if (c.url.endsWith('/api/me/mfa/step-up')) return served('step_up_success')
      return undefined
    })
    render(<LangProvider><PharmacyPage /></LangProvider>)
    const user = userEvent.setup()
    await user.click(await screen.findByTestId('queue-item'))
    await user.click(await screen.findByTestId('dispense-button'))
    const dialog = await screen.findByRole('dialog')
    await user.type(within(dialog).getByLabelText('رمز التحقق'), CODE)
    await user.click(within(dialog).getByRole('button', { name: 'تحقق' }))
    expect(await screen.findByTestId('dispense-notice')).toBeInTheDocument()
    expect(count('POST', '/dispense')).toBe(2)
  })

  it('the prompt is Arabic and right-to-left by default, keyboard-operable, and Escape cancels without a retry', async () => {
    stub(c => {
      if (c.method === 'POST' && c.url.endsWith('/api/prescriptions')) return served('prescribe_without_step_up')
      return vetDefaults(c)
    })
    render(<LangProvider><VetPrescriptionsPage /></LangProvider>)
    const user = userEvent.setup()
    await issuePrescription(user)
    const dialog = await screen.findByRole('dialog')
    expect(dialog).toHaveAttribute('dir', 'rtl')
    expect(dialog).toHaveAttribute('aria-modal', 'true')
    expect(dialog.textContent).not.toMatch(/[A-Za-z]/)                        // no English string in Arabic mode
    const buttons = within(dialog).getAllByRole('button')
    buttons[buttons.length - 1].focus()
    await user.tab()
    expect(dialog.contains(document.activeElement)).toBe(true)               // focus stays in the prompt
    await user.keyboard('{Escape}')
    await waitFor(() => expect(screen.queryByRole('dialog')).toBeNull())
    expect(count('POST', '/api/prescriptions')).toBe(1)
  })
})

describe('Lane B — enrolment (served contract)', () => {
  it('factorless enrolment presents primary re-authentication; the ten codes are shown once and never again', async () => {
    stub((c, n) => {
      if (c.url.endsWith('/api/me/mfa/enrol')) {
        const body = JSON.parse(c.body || '{}')
        if (!body.password) return served('enrol_factorless_without_password')
        return body.password === 'pw' ? served('enrol_success') : served('enrol_factorless_wrong_password')
      }
      if (c.url.endsWith('/api/me/mfa/confirm')) return n === 1 ? served('confirm_wrong_code') : served('confirm_success')
      return undefined
    })
    render(<LangProvider><SecurityPage /></LangProvider>)
    const user = userEvent.setup()
    expect(screen.getByRole('main')).toHaveAttribute('dir', 'rtl')
    expect(screen.getByRole('main').textContent).not.toMatch(/[A-Za-z]/)      // Arabic default, no English leak
    await user.click(screen.getByTestId('mfa-start'))
    const reauth = await screen.findByTestId('mfa-reauth')                     // primary re-authentication, not a prompt
    expect(screen.queryByRole('dialog')).toBeNull()
    await user.type(within(reauth).getByLabelText('كلمة المرور'), 'nope')
    await user.click(within(reauth).getByRole('button', { name: 'متابعة' }))
    expect(await screen.findByTestId('mfa-error')).toHaveTextContent('كلمة المرور غير صحيحة')
    await user.type(within(screen.getByTestId('mfa-reauth')).getByLabelText('كلمة المرور'), 'pw')
    await user.click(within(screen.getByTestId('mfa-reauth')).getByRole('button', { name: 'متابعة' }))
    const confirm = await screen.findByTestId('mfa-confirm')
    expect(within(confirm).getByTestId('mfa-key')).toHaveTextContent('SYNTHETICSECRET')
    await user.type(within(confirm).getByLabelText('رمز التحقق'), '000000')
    await user.click(within(confirm).getByRole('button', { name: 'تأكيد' }))
    await user.type(within(await screen.findByTestId('mfa-confirm')).getByLabelText('رمز التحقق'), CODE)
    await user.click(within(screen.getByTestId('mfa-confirm')).getByRole('button', { name: 'تأكيد' }))
    const list = await screen.findByTestId('mfa-code-list')
    expect(within(list).getAllByRole('listitem')).toHaveLength(10)
    expect(document.body.innerHTML).not.toContain('SYNTHETICSECRET')          // the secret is gone once confirmed
    await user.click(screen.getByTestId('mfa-codes-saved'))
    expect(await screen.findByTestId('mfa-done')).toBeInTheDocument()
    expect(document.body.innerHTML).not.toContain('TEST-CODE-0001')           // never re-displayed
    expect(screen.queryByTestId('mfa-code-list')).toBeNull()
    expect(JSON.stringify({ ...localStorage, ...sessionStorage })).not.toContain('TEST-CODE')
    expect(count('POST', '/api/me/mfa/confirm')).toBe(2)
  })

  it('replacing an active factor presents existing-factor step-up, not the password form', async () => {
    stub((c, n) => {
      if (c.url.endsWith('/api/me/mfa/enrol')) return n === 1 ? served('replace_factor_without_step_up') : served('enrol_success')
      if (c.url.endsWith('/api/me/mfa/step-up')) return served('step_up_success')
      return undefined
    })
    render(<LangProvider><SecurityPage /></LangProvider>)
    const user = userEvent.setup()
    await user.click(screen.getByTestId('mfa-start'))
    const dialog = await screen.findByRole('dialog')
    expect(screen.queryByTestId('mfa-reauth')).toBeNull()
    await user.type(within(dialog).getByLabelText('رمز التحقق'), CODE)
    await user.click(within(dialog).getByRole('button', { name: 'تحقق' }))
    expect(await screen.findByTestId('mfa-confirm')).toBeInTheDocument()
    expect(count('POST', '/api/me/mfa/enrol')).toBe(2)
  })
})
