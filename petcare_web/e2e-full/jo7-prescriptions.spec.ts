/**
 * J-O7 — an owner views the prescriptions issued for their pet and its health timeline, and uploads a prescription written
 * elsewhere for verification (CO-11; CO-03 timeline). Full stack: browser -> petcare_web -> main:app -> PostgreSQL; no
 * MyVetiCare API is mocked. The veterinarian (console = D3) issues the prescription and reads the verification queue through
 * their own API session; deciding an upload is J-V6 (D3). No regulatory determination is involved.
 */
import { request as pwRequest, APIRequestContext } from '@playwright/test'
import { test, expect, newOwner, dismissFirstRun, untranslated, totp, USERS, SEED_PASSWORD } from './fixtures'

const API = process.env.PETCARE_E2E_API ?? 'http://localhost:8090'
const PNG = Buffer.from('89504e470d0a1a0a0000000d4948445200000001000000010806000000' +
  '1f15c4890000000d49444154789c6360000002000154a24f5d0000000049454e44ae426082', 'hex')

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

test('[J-O7] @S:CO-11 an owner views their pet\'s prescriptions and timeline and uploads one for verification', async ({ page, lang }, info) => {
  await newOwner(page, info, 'jo7', lang)
  const petName = lang === 'ar' ? 'لونا' : 'Luna'
  const pet = await page.request.post(`${API}/api/pets`, { data: { name: petName, species: 'cat' } })
  expect(pet.status()).toBe(200)
  const petId = (await pet.json()).pet_id as string
  const vet = await staff(USERS.vet)
  await stepUp(vet)
  const medication = lang === 'ar' ? 'أموكسيسيلين' : 'Amoxicillin'
  const rx = await vet.post('/api/prescriptions', { data: { pet_id: petId, session_id: 's-jo7', medication_name: medication,
    dosage: '50mg', instructions: lang === 'ar' ? 'مرتين يومياً' : 'Twice a day' } })
  expect(rx.status(), await rx.text()).toBe(200)
  // Another owner's pet in the same clinic gets a prescription too: it must never appear in this owner's list
  const admin = await staff(USERS.platformAdmin)
  const otherPet = await admin.post('/api/pets', { data: { name: 'Other', species: 'dog', owner_id: 'u-e2e-owner' } })
  expect(otherPet.status(), await otherPet.text()).toBe(200)
  await stepUp(vet)
  const otherRx = await vet.post('/api/prescriptions', { data: { pet_id: (await otherPet.json()).pet_id, session_id: 's-jo7-other',
    medication_name: 'Doxycycline', dosage: '10mg', instructions: 'once' } })
  expect(otherRx.status(), await otherRx.text()).toBe(200)
  await admin.dispose()

  // Reached from the owner home
  await page.goto('/owner')
  await page.waitForLoadState('networkidle')
  await dismissFirstRun(page)
  await page.getByTestId('owner-open-prescriptions').click()
  await expect(page).toHaveURL(/\/owner\/prescriptions$/)
  const item = page.getByTestId('owner-prescription')
  await expect(item).toHaveCount(1)
  await expect(item).toContainText(medication)
  await expect(item).toHaveAttribute('data-status', 'ISSUED')
  await expect(page.getByTestId('owner-upload')).toHaveCount(0)
  if (lang === 'ar') expect(await untranslated(page, 'main')).toEqual([])

  // Upload a prescription from another clinic; the server holds it awaiting verification
  await page.getByTestId('upload-file').setInputFiles({ name: 'external-rx.png', mimeType: 'image/png', buffer: PNG })
  await page.locator('textarea[name="note"]').fill(lang === 'ar' ? 'من عيادة سابقة' : 'From the previous clinic')
  await page.getByTestId('upload-submit').click()
  await expect(page.getByTestId('upload-done')).toBeVisible()
  const up = page.getByTestId('owner-upload')
  await expect(up).toHaveCount(1)
  await expect(up).toHaveAttribute('data-status', 'AWAITING_VERIFICATION')
  const file = await page.request.get((await up.getByTestId('owner-upload-download').getAttribute('href')) as string)
  expect(Buffer.from(await file.body()).equals(PNG)).toBe(true)
  const queue = await (await vet.get('/api/prescriptions/uploads/awaiting-verification')).json()
  expect(queue.some((u: { pet_id: string }) => u.pet_id === petId)).toBe(true)
  if (lang === 'ar') expect(await untranslated(page, 'main')).toEqual([])

  // The pet's health timeline (CO-03) is one click away
  await page.getByTestId('prescription-timeline').click()
  await expect(page).toHaveURL(/\/owner\/pets/)
  await vet.dispose()
})
