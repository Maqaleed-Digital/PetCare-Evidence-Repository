/**
 * CO-06 — an owner sends the pre-visit intake with photos for an upcoming appointment (MVC-EPC-D-001 D2p, R21.4: remaining owner
 * screens). Full stack: browser -> petcare_web -> main:app -> PostgreSQL + the governed document store (local mode, as CO-11);
 * no MyVetiCare API is mocked and no provider is involved. The booking is made through the owner's own API session (J-O5 is
 * already proven through its screens); the veterinarian (console = D3) reads the intake through their own API session.
 */
import { request as pwRequest, APIRequestContext } from '@playwright/test'
import { test, expect, newOwner, dismissFirstRun, untranslated, USERS, SEED_PASSWORD } from './fixtures'

const API = process.env.PETCARE_E2E_API ?? 'http://localhost:8090'
const PNG = Buffer.from('89504e470d0a1a0a0000000d4948445200000001000000010806000000' +
  '1f15c4890000000d49444154789c6360000002000154a24f5d0000000049454e44ae426082', 'hex')
const JPG = Buffer.concat([Buffer.from([0xff, 0xd8, 0xff, 0xe0]), Buffer.alloc(64), Buffer.from([0xff, 0xd9])])

async function staff(email: string): Promise<APIRequestContext> {
  const probe = await pwRequest.newContext({ baseURL: API })
  const r = await probe.post('/api/auth/sign-in', { data: { email, password: SEED_PASSWORD } })
  expect(r.status(), await r.text()).toBe(200)
  const cookie = r.headersArray().filter(h => h.name.toLowerCase() === 'set-cookie')
    .map(h => h.value.split(';')[0]).find(v => v.startsWith('petcare_session='))
  await probe.dispose()
  return pwRequest.newContext({ baseURL: API, extraHTTPHeaders: { cookie: cookie as string } })
}

test('@S:CO-06 an owner sends the pre-visit intake with photos for an upcoming appointment', async ({ page, lang }, info) => {
  await newOwner(page, info, 'co06', lang)
  const pet = await page.request.post(`${API}/api/pets`, { data: { name: lang === 'ar' ? 'لونا' : 'Luna', species: 'cat' } })
  expect(pet.status()).toBe(200)
  const petId = (await pet.json()).pet_id as string
  const vetId = ((await (await page.request.get(`${API}/api/booking/veterinarians`)).json()) as { user_id: string }[])[0].user_id
  let slot: string | undefined
  for (let d = 1; d <= 10 && !slot; d++) {
    const day = new Date(Date.now() + d * 86_400_000).toISOString().slice(0, 10)
    slot = ((await (await page.request.get(`${API}/api/booking/slots?veterinarian_id=${vetId}&day=${day}`)).json()) as string[])[0]
  }
  const booked = await page.request.post(`${API}/api/bookings`, { data: { pet_id: petId, veterinarian_id: vetId, starts_at: slot } })
  expect(booked.status(), await booked.text()).toBe(201)
  const bookingId = (await booked.json()).booking_id as string

  // Reached from the owner home -> my appointments -> the appointment's intake
  await page.goto('/owner')
  await page.waitForLoadState('networkidle')
  await dismissFirstRun(page)
  await page.getByTestId('owner-open-appointments').click()
  await expect(page).toHaveURL(/\/owner\/appointments$/)
  await page.getByTestId('appointment-intake').click()
  await expect(page).toHaveURL(new RegExp(`/owner/appointments/${bookingId}/intake$`))

  const reason = lang === 'ar' ? 'يعرج على الساق الخلفية اليسرى' : 'Limping on the left hind leg'
  const meds = lang === 'ar' ? 'لا شيء' : 'None'
  const form = page.getByTestId('intake-form')
  await expect(form).toBeVisible()
  if (lang === 'ar') expect(await untranslated(page, 'main')).toEqual([])
  await form.locator('textarea[name="reason"]').fill(reason)
  await form.locator('input[name="symptoms_since"]').fill(new Date(Date.now() - 3 * 86_400_000).toISOString().slice(0, 10))
  await form.locator('input[name="eating_normally"][value="NO"]').check()
  await form.locator('textarea[name="current_medications"]').fill(meds)
  await page.getByTestId('intake-photos').setInputFiles([
    { name: 'leg.png', mimeType: 'image/png', buffer: PNG }, { name: 'paw.jpg', mimeType: 'image/jpeg', buffer: JPG }])
  await page.getByTestId('intake-submit').click()

  await expect(page.getByTestId('intake-done')).toBeVisible()
  await expect(page.getByTestId('intake-reason')).toHaveText(reason)
  await expect(page.getByTestId('intake-eating')).toHaveAttribute('data-value', 'NO')
  const photos = page.getByTestId('intake-photo')
  await expect(photos).toHaveCount(2)
  const href = (await photos.first().getByTestId('intake-photo-download').getAttribute('href')) as string
  expect(Buffer.from(await (await page.request.get(href)).body()).equals(PNG)).toBe(true)
  if (lang === 'ar') expect(await untranslated(page, 'main')).toEqual([])

  // The server kept it — not the tab — and it is sent once
  await page.reload()
  await page.waitForLoadState('networkidle')
  await expect(page.getByTestId('intake-submitted')).toBeVisible()
  await expect(page.getByTestId('intake-form')).toHaveCount(0)
  const again = await page.request.post(`${API}/api/bookings/${bookingId}/intake`,
    { multipart: { reason: 'second', eating_normally: 'YES' } })
  expect(again.status()).toBe(409)

  // The veterinarian of the clinic reads exactly what the owner sent
  const vet = await staff(USERS.vet)
  const seen = await (await vet.get(`/api/bookings/${bookingId}/intake`)).json()
  expect(seen.reason).toBe(reason)
  expect((seen.photos as { filename: string }[]).map(p => p.filename)).toEqual(['leg.png', 'paw.jpg'])
  await vet.dispose()
})
