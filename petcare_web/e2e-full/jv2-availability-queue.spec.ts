/**
 * J-V2 — a veterinarian publishes their availability and works from their queue (MVC-EPC-D-001 D3b, R21.4; CV-02, CV-03).
 * Full stack: browser -> petcare_web -> main:app -> PostgreSQL; nothing is mocked and no provider is involved. The veterinarian
 * uses the console screens; the owner side (slots, booking) is the seeded owner's own API session — J-O5 already proves the
 * owner's booking screens. The CI run serves every project from one stack, so each project uses its own hour, and the spec ends
 * by republishing a full week so later journeys keep the clinic's hours.
 */
import { request as pwRequest, APIRequestContext } from '@playwright/test'
import { test, expect, signIn, untranslated, USERS, SEED_PASSWORD } from './fixtures'

const API = process.env.PETCARE_E2E_API ?? 'http://localhost:8090'
const HOUR: Record<string, number> = { 'ar-desktop': 10, 'ar-mobile': 11, 'en-desktop': 12, 'en-mobile': 13 }
const RIYADH_MS = 3 * 3_600_000

async function session(email: string): Promise<APIRequestContext> {
  const probe = await pwRequest.newContext({ baseURL: API })
  const r = await probe.post('/api/auth/sign-in', { data: { email, password: SEED_PASSWORD } })
  expect(r.status(), await r.text()).toBe(200)
  const cookie = r.headersArray().filter(h => h.name.toLowerCase() === 'set-cookie')
    .map(h => h.value.split(';')[0]).find(v => v.startsWith('petcare_session='))
  await probe.dispose()
  return pwRequest.newContext({ baseURL: API, extraHTTPHeaders: { cookie: cookie as string } })
}

test('[J-V2] @S:CV-02 @S:CV-03 a veterinarian publishes availability; owners book only those slots; the booking is in their queue', async ({ page, lang }, info) => {
  const h = HOUR[info.project.name]
  const pad = (n: number) => String(n).padStart(2, '0')
  // a Riyadh calendar day three days ahead, and its Python weekday (0 = Monday)
  const day = new Date(Date.now() + RIYADH_MS + 3 * 86_400_000).toISOString().slice(0, 10)
  const weekday = (new Date(`${day}T12:00:00Z`).getUTCDay() + 6) % 7

  // CV-02: the veterinarian publishes one working day, one hour
  await signIn(page, USERS.vet)
  await expect(page).toHaveURL(/\/vet/)
  await page.goto('/vet')
  await page.getByTestId('vet-open-availability').click()
  await expect(page).toHaveURL(/\/vet\/availability$/)
  const form = page.getByTestId('availability-form')
  await expect(form).toBeVisible()
  for (let d = 0; d < 7; d++) {
    const box = form.locator(`input[name="works-${d}"]`)
    if ((d === weekday) !== (await box.isChecked())) await box.click()
  }
  await form.locator(`select[name="opens-${weekday}"]`).selectOption(`${pad(h)}:00`)
  await form.locator(`select[name="closes-${weekday}"]`).selectOption(`${pad(h + 1)}:00`)
  if (lang === 'ar') expect(await untranslated(page, 'main')).toEqual([])
  await page.getByTestId('availability-publish').click()
  await expect(page.getByTestId('availability-published')).toBeVisible()
  await expect(page.locator(`[data-testid="availability-day"][data-works="true"]`)).toHaveCount(1)

  // The owner can book only inside the published hour
  const owner = await session(USERS.owner)
  const pet = await owner.post('/api/pets', { data: { name: lang === 'ar' ? 'لونا' : 'Luna', species: 'cat' } })
  const petId = (await pet.json()).pet_id as string
  const slots = (await (await owner.get(`/api/booking/slots?veterinarian_id=u-e2e-vet&day=${day}`)).json()) as string[]
  const local = slots.map(s => new Date(new Date(s).getTime() + RIYADH_MS).toISOString().slice(11, 16))
  expect(local).toEqual([`${pad(h)}:00`, `${pad(h)}:30`])
  const outside = await owner.post('/api/bookings', { data: { pet_id: petId, veterinarian_id: 'u-e2e-vet', starts_at: `${day}T09:00:00+03:00` } })
  expect(outside.status()).toBe(400)
  const booked = await owner.post('/api/bookings', { data: { pet_id: petId, veterinarian_id: 'u-e2e-vet', starts_at: slots[1],
    reason: lang === 'ar' ? 'فحص دوري' : 'Routine check' } })
  expect(booked.status(), await booked.text()).toBe(201)
  const bookingId = (await booked.json()).booking_id as string
  await owner.dispose()

  // CV-03: the booking is in the veterinarian's queue, with its pet and owner
  await page.goto('/vet')
  await page.getByTestId('vet-open-queue').click()
  await expect(page).toHaveURL(/\/vet\/queue$/)
  const row = page.locator(`[data-testid="queue-appointment"][data-booking="${bookingId}"]`)
  await expect(row).toBeVisible()
  await expect(row).toContainText(lang === 'ar' ? 'لونا' : 'Luna')
  await expect(row).toContainText('مالك تجريبي')                        // the seeded owner's name (tools/e2e_stack.py)
  await expect(row).toHaveAttribute('data-intake', 'false')
  if (lang === 'ar') {
    await expect(page.locator('main')).toHaveAttribute('dir', 'rtl')
    expect(await untranslated(page, 'main')).toEqual([])
  }

  // Republish a full week (09:00-17:00): later journeys keep the clinic's hours; the booking is unchanged by it
  const full = Array.from({ length: 7 }, (_, d) => ({ weekday: d, opens: '09:00', closes: '17:00' }))
  expect((await page.request.put(`${API}/api/vet/availability`, { data: { windows: full } })).status()).toBe(200)
  await page.reload()
  await expect(page.locator(`[data-testid="queue-appointment"][data-booking="${bookingId}"]`)).toBeVisible()
})
