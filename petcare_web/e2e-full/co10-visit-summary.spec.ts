/**
 * CO-10 — an owner reads the visit summary and care plan of their completed consultation (MVC-EPC-D-001 D2q, R21.4: remaining
 * owner screens). Full stack: browser -> petcare_web -> main:app -> PostgreSQL; no MyVetiCare API is mocked and no provider is
 * involved. The veterinarian (console = D3) starts the consultation, records its outcome, prescribes under it (SQ-3 step-up with
 * the per-run seeded factor, as J-O7) and records the care plan, all through their own API session.
 */
import { request as pwRequest, APIRequestContext } from '@playwright/test'
import { test, expect, newOwner, dismissFirstRun, untranslated, totp, USERS, SEED_PASSWORD } from './fixtures'

const API = process.env.PETCARE_E2E_API ?? 'http://localhost:8090'
const VET_NAME = 'طبيب تجريبي'          // the seeded veterinarian's full name (tools/e2e_stack.py USERS)

async function staff(email: string): Promise<APIRequestContext> {
  const probe = await pwRequest.newContext({ baseURL: API })
  const r = await probe.post('/api/auth/sign-in', { data: { email, password: SEED_PASSWORD } })
  expect(r.status(), await r.text()).toBe(200)
  const cookie = r.headersArray().filter(h => h.name.toLowerCase() === 'set-cookie')
    .map(h => h.value.split(';')[0]).find(v => v.startsWith('petcare_session='))
  await probe.dispose()
  return pwRequest.newContext({ baseURL: API, extraHTTPHeaders: { cookie: cookie as string } })
}

/** SQ-3: the veterinarian steps up with the per-run TOTP factor the stack seeded (tools/e2e_stack.py, never in the repo). */
async function stepUp(vet: APIRequestContext) {
  const fs = await import('node:fs')
  const file = (process.env.PETCARE_E2E_OUTBOX as string).replace(/\.jsonl$/, '.mfa.json')
  const key = JSON.parse(fs.readFileSync(file, 'utf8'))['u-e2e-vet'] as string
  for (let attempt = 0; attempt < 4; attempt++) {
    for (const offset of [0, 30_000]) {
      const r = await vet.post('/api/me/mfa/step-up', { data: { code: await totp(key, Date.now() + offset) } })
      if (r.status() === 200) return
    }
    await new Promise(res => setTimeout(res, 31_000 - (Date.now() % 30_000)))   // that step was spent: wait for the next
  }
  throw new Error('step-up refused')
}

test('@S:CO-10 an owner reads the visit summary and care plan of their completed consultation', async ({ page, lang }, info) => {
  await newOwner(page, info, 'co10', lang)
  const me = await (await page.request.get(`${API}/api/auth/me`)).json()
  const petName = lang === 'ar' ? 'لونا' : 'Luna'
  const pet = await page.request.post(`${API}/api/pets`, { data: { name: petName, species: 'cat' } })
  expect(pet.status()).toBe(200)
  const petId = (await pet.json()).pet_id as string

  const vet = await staff(USERS.vet)
  const start = async () => {
    const r = await vet.post('/api/consultations', { data: { pet_id: petId, owner_id: me.user_id, veterinarian_id: 'u-e2e-vet' } })
    expect(r.status(), await r.text()).toBe(200)
    return (await r.json()).session_id as string
  }
  const sid = await start()
  const open = await start()                                   // a second, not yet completed consultation
  const outcome = lang === 'ar' ? 'التواء بسيط في الساق الخلفية؛ راحة ومضاد التهاب.' : 'Mild sprain of the hind leg; rest and anti-inflammatory.'
  expect((await vet.post(`/api/consultations/${sid}/outcome`, { data: { outcome } })).status()).toBe(200)
  const medication = lang === 'ar' ? 'ميلوكسيكام' : 'Meloxicam'
  const dosing = lang === 'ar' ? 'مرة يومياً مع الطعام' : 'Once daily with food'
  await stepUp(vet)
  const rx = await vet.post('/api/prescriptions', { data: { pet_id: petId, session_id: sid, medication_name: medication,
    dosage: lang === 'ar' ? '٠٫٥ ملغ' : '0.5 mg', instructions: dosing } })
  expect(rx.status(), await rx.text()).toBe(200)
  const plan = lang === 'ar' ? 'راحة لمدة سبعة أيام؛ دون قفز أو جري.' : 'Rest for seven days; no jumping or running.'
  const followUp = new Date(Date.now() + 14 * 86_400_000).toISOString().slice(0, 10)
  const recorded = await vet.post(`/api/consultations/${sid}/care-plan`, { data: { instructions: plan, follow_up_on: followUp } })
  expect(recorded.status(), await recorded.text()).toBe(201)
  expect((await vet.post(`/api/consultations/${open}/care-plan`, { data: { instructions: plan } })).status()).toBe(409)

  // Reached from the owner home -> my consultations -> the completed visit
  await page.goto('/owner')
  await page.waitForLoadState('networkidle')
  await dismissFirstRun(page)
  await page.getByTestId('owner-open-consultations').click()
  await expect(page).toHaveURL(/\/owner\/consultations$/)
  await expect(page.getByTestId('owner-consultation')).toHaveCount(2)
  await expect(page.locator('[data-testid="owner-consultation"][data-status="REQUESTED"]').getByTestId('consultation-open-summary')).toHaveCount(0)
  await page.locator('[data-testid="owner-consultation"][data-status="COMPLETED"]').getByTestId('consultation-open-summary').click()
  await expect(page).toHaveURL(new RegExp(`/owner/consultations/${sid}/summary$`))

  await expect(page.getByTestId('visit-summary')).toBeVisible()
  await expect(page.getByTestId('visit-outcome')).toHaveText(outcome)
  await expect(page.getByTestId('visit-vet')).toHaveText(VET_NAME)
  await expect(page.getByTestId('visit-prescription')).toHaveCount(1)
  await expect(page.getByTestId('visit-prescription')).toContainText(medication)
  await expect(page.getByTestId('visit-prescription')).toContainText(dosing)
  await expect(page.getByTestId('care-plan-instructions')).toHaveText(plan)
  await expect(page.getByTestId('care-plan-follow-up')).toHaveAttribute('data-date', followUp)
  if (lang === 'ar') {
    await expect(page.locator('main')).toHaveAttribute('dir', 'rtl')
    expect(await untranslated(page, 'main')).toEqual([])
  }

  // The visit still open has no summary; an unknown visit is never confirmed
  await page.goto(`/owner/consultations/${open}/summary`)
  await expect(page.getByTestId('visit-not-completed')).toBeVisible()
  expect((await page.request.get(`${API}/api/owner/consultations/not-a-session/summary`)).status()).toBe(404)
  await vet.dispose()
})
