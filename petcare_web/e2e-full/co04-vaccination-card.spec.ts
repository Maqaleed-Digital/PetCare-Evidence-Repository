/**
 * CO-04 — an owner opens their pet's vaccination card and saves it as a PDF (MVC-EPC-D-001 D2o, R21.4: remaining owner screens).
 * Full stack: browser -> petcare_web -> main:app -> PostgreSQL; no MyVetiCare API is mocked and no provider is involved. The
 * veterinarian (console = D3) records the vaccinations through their own API session (FR-23). The PDF is produced by the
 * browser's print engine from the page (Chromium `page.pdf`, the same engine as "Save as PDF").
 */
import { request as pwRequest, APIRequestContext } from '@playwright/test'
import { test, expect, newOwner, dismissFirstRun, untranslated, USERS, SEED_PASSWORD } from './fixtures'

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

async function due(vet: APIRequestContext, petId: string, title: string, inDays: number, kind = 'VACCINATION') {
  const r = await vet.post(`/api/pets/${petId}/care-due`,
    { data: { kind, title, due_at: new Date(Date.now() + inDays * 86_400_000).toISOString() } })
  expect(r.status(), await r.text()).toBe(200)
  return (await r.json()).due_id as string
}

test('@S:CO-04 an owner opens their pet\'s vaccination card and saves it as PDF', async ({ page, lang }, info) => {
  await newOwner(page, info, 'co04', lang)
  const petName = lang === 'ar' ? 'لونا' : 'Luna'
  const pet = await page.request.post(`${API}/api/pets`, { data: { name: petName, species: lang === 'ar' ? 'قطة' : 'cat' } })
  expect(pet.status()).toBe(200)
  const petId = (await pet.json()).pet_id as string

  const vet = await staff(USERS.vet)
  const rabies = lang === 'ar' ? 'داء الكلب' : 'Rabies'
  const booster = lang === 'ar' ? 'جرعة معززة' : 'FVRCP booster'
  const given = await due(vet, petId, rabies, -1)
  expect((await vet.post(`/api/pets/${petId}/care-due/${given}/complete`)).status()).toBe(200)
  await due(vet, petId, booster, 30)
  await due(vet, petId, lang === 'ar' ? 'مضاد الديدان' : 'Deworming', 5, 'TREATMENT')      // a treatment: never on the card

  // Another owner's pet in the same clinic, with its own vaccination: never readable by this owner
  const admin = await staff(USERS.platformAdmin)
  const other = await admin.post('/api/pets', { data: { name: 'Other', species: 'dog', owner_id: 'u-e2e-owner' } })
  expect(other.status(), await other.text()).toBe(200)
  const otherId = (await other.json()).pet_id as string
  await due(vet, otherId, 'Other vaccine', 3)
  expect((await page.request.get(`${API}/api/pets/${otherId}/vaccination-card`)).status()).toBe(404)
  await admin.dispose()

  // Reached from the owner home -> my pets -> the pet's profile
  await page.goto('/owner')
  await page.waitForLoadState('networkidle')
  await dismissFirstRun(page)
  await page.getByTestId('owner-open-pets').click()
  await expect(page).toHaveURL(/\/owner\/pets$/)
  await page.getByRole('button', { name: new RegExp(`^${petName} · `) }).click()
  await page.getByTestId('pet-vaccination-card').click()
  await expect(page).toHaveURL(new RegExp(`/owner/pets/${petId}/vaccination-card$`))

  const card = page.getByTestId('vaccination-card')
  await expect(card).toBeVisible()
  await expect(card.getByRole('heading', { name: petName })).toBeVisible()
  const givenRows = page.getByTestId('vaccination-given')
  await expect(givenRows).toHaveCount(1)
  await expect(givenRows).toContainText(rabies)
  await expect(givenRows).toContainText(VET_NAME)
  const dueRows = page.getByTestId('vaccination-due')
  await expect(dueRows).toHaveCount(1)
  await expect(dueRows).toContainText(booster)
  await expect(card).not.toContainText(lang === 'ar' ? 'مضاد الديدان' : 'Deworming')
  await expect(card).not.toContainText('Other vaccine')
  if (lang === 'ar') {
    await expect(page.locator('main')).toHaveAttribute('dir', 'rtl')
    expect(await untranslated(page, 'main')).toEqual([])
  }

  // Printed / saved as PDF: the card stays, the actions and site chrome are dropped
  await page.emulateMedia({ media: 'print' })
  await expect(card).toBeVisible()
  await expect(page.getByTestId('vaccination-card-print')).toBeHidden()
  const pdf = await page.pdf({ format: 'A4' })
  expect(pdf.subarray(0, 5).toString('latin1')).toBe('%PDF-')
  expect(pdf.length).toBeGreaterThan(1000)
  await page.emulateMedia({ media: 'screen' })
  await vet.dispose()
})
