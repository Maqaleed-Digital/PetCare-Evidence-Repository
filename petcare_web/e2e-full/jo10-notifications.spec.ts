/**
 * J-O10 — care reminders reach the owner's notification centre only with their consent (CO-01 owner home, CO-14
 * notifications). Full stack: browser -> petcare_web -> main:app -> PostgreSQL. The veterinarian records the due date
 * and the clinic administrator runs the served FR-23 scheduler through their own API sessions; everything the owner
 * does is through the served screens. Delivery is IN_APP — no provider is reached (Sponsor ruling R10: consent is
 * enforced at dispatch, so the first run must withhold and the second, after consent, must deliver).
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
  expect(cookie).toBeTruthy()
  await probe.dispose()
  return pwRequest.newContext({ baseURL: API, extraHTTPHeaders: { cookie: cookie as string } })
}

test('[J-O10] @S:CO-01 @S:CO-14 care reminders reach the notification centre only once the owner consents', async ({ page, lang }, info) => {
  await newOwner(page, info, 'jo10', lang)
  const me = await (await page.request.get(`${API}/api/auth/me`)).json()
  expect((await page.request.put(`${API}/api/me/preferences/language`, { data: { language: lang } })).status()).toBe(200)
  const pet = await page.request.post(`${API}/api/pets`, { data: { name: lang === 'ar' ? 'لونا' : 'Luna', species: 'cat' } })
  expect(pet.status()).toBe(200)
  const petId = (await pet.json()).pet_id as string

  const vet = await staff(USERS.vet)
  const admin = await staff(USERS.clinicAdmin)
  const dueAt = new Date(Date.now() + 72 * 3600_000).toISOString()
  // The veterinarian writes the item in the clinic's language; the X1 scan below still inspects everything shown.
  const title = lang === 'ar' ? 'جرعة داء الكلب المعززة' : 'Rabies booster'
  const due = await vet.post(`/api/pets/${petId}/care-due`, { data: { kind: 'VACCINATION', title, due_at: dueAt } })
  expect(due.status(), await due.text()).toBe(200)
  const dueId = (await due.json()).due_id as string

  // 1. No care_reminders consent yet: the served scheduler withholds, and the centre shows its empty state.
  const first = await (await admin.post('/api/reminders/run')).json()
  expect(first.sent.filter((s: { due_id: string }) => s.due_id === dueId)).toEqual([])
  expect(first.withheld).toContainEqual({ due_id: dueId, owner_id: me.user_id, reason: 'CONSENT_ABSENT' })
  await page.goto('/owner/notifications')
  await page.waitForLoadState('networkidle')
  await expect(page.getByTestId('notifications-page').locator('[data-state="empty"]')).toBeVisible()
  await expect(page.getByTestId('notification')).toHaveCount(0)

  // 2. The owner grants care reminders on the served account centre (server ledger, not the browser).
  await page.goto('/account')
  await page.waitForLoadState('networkidle')
  await page.getByTestId('consent-care_reminders-grant').click()
  await expect(page.getByTestId('consent-care_reminders')).toHaveAttribute('data-granted', 'true')

  // 3. The next run delivers it — once.
  const second = await (await admin.post('/api/reminders/run')).json()
  expect(second.sent).toContainEqual({ due_id: dueId, kind: 'REMIND_7D', owner_id: me.user_id, language: lang })
  const third = await (await admin.post('/api/reminders/run')).json()
  expect(third.sent.filter((s: { due_id: string }) => s.due_id === dueId)).toEqual([])

  // 4. From the owner home (CO-01) to the notification centre (CO-14): the reminder, in the owner's language.
  await page.goto('/owner')
  await page.waitForLoadState('networkidle')
  await dismissFirstRun(page)                        // Esc closes the guide for this visit only (by design); it returns
  await page.getByTestId('owner-open-notifications').click()
  await expect(page).toHaveURL(/\/owner\/notifications$/)
  const item = page.getByTestId('notification')
  await expect(item).toHaveCount(1)
  await expect(item).toHaveAttribute('data-kind', 'reminder')
  const body = item.locator('p')
  if (lang === 'ar') {
    await expect(body).toContainText('تذكير')
    expect(await untranslated(page, 'main')).toEqual([])
  } else {
    await expect(body).toContainText('Reminder: within 7 days')
  }
  await item.getByRole('link').click()
  await expect(page).toHaveURL(/\/owner\/reminders$/)

  await vet.dispose()
  await admin.dispose()
})
