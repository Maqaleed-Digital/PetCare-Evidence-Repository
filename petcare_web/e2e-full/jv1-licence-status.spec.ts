/**
 * J-V1 internal portion — a veterinarian joins by invite with their licence, and sees its status until it is verified
 * (MVC-EPC-D-001 D3a, R21.4; CV-12). Full stack: browser -> petcare_web -> main:app -> PostgreSQL; nothing is mocked.
 *
 * Tagged [J-V1-INTERNAL], which report.mjs does not count, and carries no screen tag: J-V1's licence verification against the
 * issuing authority's registry is the open external dependency X-33 (R19.3 — a staff attestation is not registry verification;
 * no mock registry may count it). The platform staff steps (tenant assignment, MANUAL_STAFF verification) are made through the
 * served admin API (the admin console is D7).
 */
import { request as pwRequest, APIRequestContext } from '@playwright/test'
import { test, expect, signIn, untranslated, totp, USERS, SEED_PASSWORD } from './fixtures'

const API = process.env.PETCARE_E2E_API ?? 'http://localhost:8090'
const TENANT = 't-e2e-clinic'

async function staff(email: string): Promise<APIRequestContext> {
  const probe = await pwRequest.newContext({ baseURL: API })
  const r = await probe.post('/api/auth/sign-in', { data: { email, password: SEED_PASSWORD } })
  expect(r.status(), await r.text()).toBe(200)
  const cookie = r.headersArray().filter(h => h.name.toLowerCase() === 'set-cookie')
    .map(h => h.value.split(';')[0]).find(v => v.startsWith('petcare_session='))
  await probe.dispose()
  return pwRequest.newContext({ baseURL: API, extraHTTPHeaders: { cookie: cookie as string } })
}

/** SQ-3: a staff member steps up with the per-run TOTP factor the stack seeded (tools/e2e_stack.py, never in the repo). */
async function stepUp(ctx: APIRequestContext, userId: string) {
  const fs = await import('node:fs')
  const file = (process.env.PETCARE_E2E_OUTBOX as string).replace(/\.jsonl$/, '.mfa.json')
  const key = JSON.parse(fs.readFileSync(file, 'utf8'))[userId] as string
  for (let attempt = 0; attempt < 4; attempt++) {
    for (const offset of [0, 30_000]) {
      const r = await ctx.post('/api/me/mfa/step-up', { data: { code: await totp(key, Date.now() + offset) } })
      if (r.status() === 200) return
    }
    await new Promise(res => setTimeout(res, 31_000 - (Date.now() % 30_000)))   // that step was spent: wait for the next
  }
  throw new Error('step-up refused')
}

test('[J-V1-INTERNAL] a veterinarian joins by invite with their licence and sees its status until staff verify it', async ({ page, lang }, info) => {
  const email = `vet.jv1.${info.project.name}.${Date.now()}@e2e.test`
  const password = 'Vet-passw0rd-1'
  const licenceNumber = `E2E-LIC-${Date.now()}`
  const expires = new Date(Date.now() + 365 * 86_400_000).toISOString().slice(0, 10)

  // Onboarding: invite registration with licence details (FR-05)
  await page.goto('/register')
  await page.waitForLoadState('networkidle')
  await page.locator('#reg-name').fill(lang === 'ar' ? 'طبيبة جديدة' : 'New Vet')
  await page.locator('#reg-email').fill(email)
  await page.locator('#reg-invite').fill(`E2E-VET-INVITE-${info.project.name}`)
  await page.locator('#reg-role').selectOption('veterinarian')
  await page.locator('#reg-licence-number').fill(licenceNumber)
  await page.locator('#reg-licence-authority').fill('MEWA')
  await page.locator('#reg-licence-expiry').fill(expires)
  await page.locator('#reg-password').fill(password)
  await page.locator('form button[type="submit"]').click()
  await expect(page).toHaveURL(/\/vet$/)

  // Licence status: submitted, no authority, registry check not available
  await page.getByTestId('vet-open-profile').click()
  await expect(page).toHaveURL(/\/vet\/profile$/)
  const lic = page.getByTestId('vet-licence')
  await expect(lic).toHaveCount(1)
  await expect(lic).toHaveAttribute('data-status', 'SUBMITTED')
  await expect(lic).toContainText(licenceNumber)
  await expect(page.getByTestId('vet-authority')).toHaveAttribute('data-in-force', 'false')
  await expect(page.getByTestId('vet-registry-notice')).toBeVisible()
  if (lang === 'ar') expect(await untranslated(page, 'main')).toEqual([])

  // Platform staff: assign the clinic, then verify the licence by a named, manual attestation
  const admin = await staff(USERS.platformAdmin)
  const me = await (await page.request.get(`${API}/api/auth/me`)).json()
  await stepUp(admin, 'u-e2e-platform-admin')
  const assigned = await admin.post(`/api/admin/identities/${me.user_id}/tenant`, { data: { tenant_id: TENANT, reason: 'E2E J-V1 onboarding' } })
  expect(assigned.status(), await assigned.text()).toBe(200)
  const pending = ((await (await admin.get('/api/admin/practitioners/licences')).json()) as { licence_id: string; licence_number: string }[])
    .find(l => l.licence_number === licenceNumber)
  expect(pending).toBeTruthy()
  await stepUp(admin, 'u-e2e-platform-admin')
  const verified = await admin.post(`/api/admin/practitioners/licences/${pending!.licence_id}/verify`,
    { data: { method: 'MANUAL_STAFF', basis: 'E2E synthetic: licence certificate sighted by staff' } })
  expect(verified.status(), await verified.text()).toBe(200)
  await admin.dispose()

  // A new session carries the clinic: the licence is verified by attestation and an authority is in force
  await signIn(page, email, password)
  await expect(page).toHaveURL(/\/vet/)
  await page.goto('/vet/profile')
  await expect(page.getByTestId('vet-licence')).toHaveAttribute('data-status', 'VERIFIED')
  await expect(page.getByTestId('vet-licence')).toHaveAttribute('data-method', 'MANUAL_STAFF')
  await expect(page.getByTestId('vet-authority')).toHaveAttribute('data-in-force', 'true')
  await expect(page.getByTestId('vet-registry-notice')).toBeVisible()
  if (lang === 'ar') {
    await expect(page.locator('main')).toHaveAttribute('dir', 'rtl')
    expect(await untranslated(page, 'main')).toEqual([])
  }

  // Leave the shared clinic as it was: the CI run serves every project from ONE stack, and later journeys (J-O5) rely on the
  // clinic's seeded veterinarian being its only one. Revocation is the governed membership change (tenant_id null).
  const cleanup = await staff(USERS.platformAdmin)
  await stepUp(cleanup, 'u-e2e-platform-admin')
  const revoked = await cleanup.post(`/api/admin/identities/${me.user_id}/tenant`, { data: { tenant_id: null, reason: 'E2E J-V1 cleanup' } })
  expect(revoked.status(), await revoked.text()).toBe(200)
  await cleanup.dispose()
})
