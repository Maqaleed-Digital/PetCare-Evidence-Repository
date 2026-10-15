/**
 * CO-13 — an owner rates their completed consultation (MVC-EPC-D-001 D2r, R21.4: remaining owner screens). Full stack:
 * browser -> petcare_web -> main:app -> PostgreSQL; no MyVetiCare API is mocked and no provider is involved. The veterinarian
 * (console = D3) starts and completes the consultation, and later reads the rating, through their own API session.
 */
import { request as pwRequest, APIRequestContext } from '@playwright/test'
import { test, expect, newOwner, dismissFirstRun, untranslated, USERS, SEED_PASSWORD } from './fixtures'

const API = process.env.PETCARE_E2E_API ?? 'http://localhost:8090'

async function staff(email: string): Promise<APIRequestContext> {
  const probe = await pwRequest.newContext({ baseURL: API })
  const r = await probe.post('/api/auth/sign-in', { data: { email, password: SEED_PASSWORD } })
  expect(r.status(), await r.text()).toBe(200)
  const cookie = r.headersArray().filter(h => h.name.toLowerCase() === 'set-cookie')
    .map(h => h.value.split(';')[0]).find(v => v.startsWith('petcare_session='))
  await probe.dispose()
  return pwRequest.newContext({ baseURL: API, extraHTTPHeaders: { cookie: cookie as string } })
}

test('@S:CO-13 an owner rates their completed consultation once', async ({ page, lang }, info) => {
  await newOwner(page, info, 'co13', lang)
  const me = await (await page.request.get(`${API}/api/auth/me`)).json()
  const pet = await page.request.post(`${API}/api/pets`, { data: { name: lang === 'ar' ? 'لونا' : 'Luna', species: 'cat' } })
  expect(pet.status()).toBe(200)
  const petId = (await pet.json()).pet_id as string
  const vet = await staff(USERS.vet)
  const start = async () => {
    const r = await vet.post('/api/consultations', { data: { pet_id: petId, owner_id: me.user_id, veterinarian_id: 'u-e2e-vet' } })
    expect(r.status(), await r.text()).toBe(200)
    return (await r.json()).session_id as string
  }
  const sid = await start()
  const open = await start()
  expect((await vet.post(`/api/consultations/${sid}/outcome`, { data: { outcome: lang === 'ar' ? 'سليم' : 'Healthy' } })).status()).toBe(200)
  expect((await page.request.post(`${API}/api/owner/consultations/${open}/rating`, { data: { score: 5 } })).status()).toBe(409)

  // Reached from the owner home -> my consultations -> the completed visit
  await page.goto('/owner')
  await page.waitForLoadState('networkidle')
  await dismissFirstRun(page)
  await page.getByTestId('owner-open-consultations').click()
  await expect(page).toHaveURL(/\/owner\/consultations$/)
  await expect(page.locator('[data-testid="owner-consultation"][data-status="REQUESTED"]').getByTestId('consultation-open-rate')).toHaveCount(0)
  await page.locator('[data-testid="owner-consultation"][data-status="COMPLETED"]').getByTestId('consultation-open-rate').click()
  await expect(page).toHaveURL(new RegExp(`/owner/consultations/${sid}/rate$`))

  const form = page.getByTestId('rate-form')
  await expect(form).toBeVisible()
  if (lang === 'ar') expect(await untranslated(page, 'main')).toEqual([])
  const comment = lang === 'ar' ? 'طبيب لطيف وشرح واضح' : 'Kind vet, clear explanation'
  await form.locator('input[name="score"][value="4"]').check()
  await form.locator('textarea[name="comment"]').fill(comment)
  await page.getByTestId('rate-submit').click()
  await expect(page.getByTestId('rate-thanks')).toBeVisible()
  await expect(page.getByTestId('rate-score')).toHaveAttribute('data-score', '4')
  await expect(page.getByTestId('rate-comment')).toHaveText(comment)
  if (lang === 'ar') {
    await expect(page.locator('main')).toHaveAttribute('dir', 'rtl')
    expect(await untranslated(page, 'main')).toEqual([])
  }

  // Held by the server, once: a reload shows it read-only and a second rating is refused
  await page.reload()
  await page.waitForLoadState('networkidle')
  await expect(page.getByTestId('rate-done')).toBeVisible()
  await expect(page.getByTestId('rate-form')).toHaveCount(0)
  expect((await page.request.post(`${API}/api/owner/consultations/${sid}/rating`, { data: { score: 1 } })).status()).toBe(409)

  // The consultation's veterinarian reads what the owner said
  const seen = await (await vet.get(`/api/consultations/${sid}/rating`)).json()
  expect([seen.score, seen.comment]).toEqual([4, comment])
  await vet.dispose()
})
