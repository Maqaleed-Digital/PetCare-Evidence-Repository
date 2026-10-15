/**
 * J-O9 — internal order tracking (MVC-EPC-D-001 D2n; Sponsor ruling R19.5 item 4; R18.4). Full stack: browser -> petcare_web ->
 * main:app -> PostgreSQL; nothing is mocked.
 *
 * An owner follows their order's own lifecycle on /owner/orders: placed -> (pharmacy assigned) -> delivered -> receipt issued,
 * from the platform's records only. The page states there is no courier tracking and never shows a carrier status or ETA.
 * Routing (FR-15) cannot assign a pharmacy in the served stack: the FR-15 routing-licence register has no served route (fixture
 * only, MVC-PHARM-001 §6c) and the served app has no maps adapter (EXTERNAL:MAPS_API). A routing request therefore records a
 * REFUSAL decision (409 NO_QUALIFYING_PHARMACY) and "pharmacy assigned" stays not done — a refusal is not a route. The assigned
 * step is proven at API level with the FR-15 contract double; nothing is mocked in this journey.
 *
 * Tagged [J-O9-INTERNAL], NOT [J-O9]: J-O9 also covers carrier readings, BLOCKED on the logistics partner (R18.4), so
 * report.mjs does not count this as J-O9 (same treatment as [J-O8-COD], R20.1).
 */
import { request as pwRequest, APIRequestContext } from '@playwright/test'
import { test, expect, newOwner, dismissFirstRun, untranslated, USERS, SEED_PASSWORD } from './fixtures'

const API = process.env.PETCARE_E2E_API ?? 'http://localhost:8090'
const GENERAL = 'e2e-shampoo'          // seeded by tools/e2e_stack.py (synthetic registration)

async function staff(email: string): Promise<APIRequestContext> {
  const probe = await pwRequest.newContext({ baseURL: API })
  const r = await probe.post('/api/auth/sign-in', { data: { email, password: SEED_PASSWORD } })
  expect(r.status(), await r.text()).toBe(200)
  const cookie = r.headersArray().filter(h => h.name.toLowerCase() === 'set-cookie')
    .map(h => h.value.split(';')[0]).find(v => v.startsWith('petcare_session='))
  await probe.dispose()
  return pwRequest.newContext({ baseURL: API, extraHTTPHeaders: { cookie: cookie as string } })
}

/** Web-first (auto-retrying) check of every step's state, in lifecycle order — waits for the page to render after a reload. */
async function expectSteps(order: import('@playwright/test').Locator, want: Record<string, boolean>) {
  const steps = order.getByTestId('tracking-step')
  await expect(steps).toHaveCount(4)
  await expect(steps.nth(0)).toHaveAttribute('data-step', 'PLACED')
  for (const [step, isDone] of Object.entries(want))
    await expect(order.locator(`[data-testid="tracking-step"][data-step="${step}"]`)).toHaveAttribute('data-done', String(isDone))
}

test('[J-O9-INTERNAL] an owner follows their order from placed to delivered and receipt, with no carrier tracking claimed', async ({ page, lang }, info) => {
  const tag = `${info.project.name}-${Date.now()}`
  await newOwner(page, info, 'jo9', lang)

  // The clinic prices the product and stocks a licensed pharmacy location (served staff routes)
  const clinic = await staff(USERS.clinicAdmin)
  expect((await clinic.post('/api/catalog/prices', { data: { product_id: GENERAL, unit_price_halalas: 1500 } })).status()).toBe(200)
  const loc = await clinic.post('/api/inventory/locations', { data: { name: `E2E pharmacy ${tag}`, latitude: 24.70, longitude: 46.68 } })
  expect(loc.status(), await loc.text()).toBe(200)
  const locationId = (await loc.json()).location_id as string
  const batch = `B-${tag}`
  expect((await clinic.post('/api/inventory/movements', { data: { location_id: locationId, product_id: GENERAL, batch,
    quantity_delta: 5, reason: 'RECEIPT', batch_expiry: '2032-06-30' } })).status()).toBe(200)
  const admin = await staff(USERS.platformAdmin)
  expect((await admin.post('/api/admin/establishment-licences', { data: { location_id: locationId,
    licence_number: `SFDA-EST-${tag}`, issuing_authority: 'SFDA', expires_on: '2099-12-31',
    basis: 'synthetic E2E entity data (R18.2)', licence_type: 'PHARMACY_ESTABLISHMENT', scope: 'veterinary medicines retail',
    evidence_document_ref: `DOC-E2E-${tag}` } })).status()).toBe(201)
  await admin.dispose()

  // The owner orders from the shop and sees it tracked as placed only
  await page.goto('/owner')
  await page.waitForLoadState('networkidle')
  await dismissFirstRun(page)
  await page.getByTestId('owner-open-orders').click()
  await expect(page).toHaveURL(/\/owner\/orders$/)
  await page.locator(`[name="qty-${GENERAL}"]`).fill('1')
  await page.locator('form button[type="submit"]').click()
  const order = page.getByTestId('order')
  await expect(order).toHaveCount(1)
  const tracking = order.getByTestId('order-tracking')
  await expect(tracking).toBeVisible()
  await expectSteps(order, { PLACED: true, ROUTED: false, DELIVERED: false, RECEIPT_ISSUED: false })
  await expect(order.getByTestId('tracking-no-carrier')).toBeVisible()
  if (lang === 'ar') expect(await untranslated(page, 'main')).toEqual([])
  const orderId = (await order.getAttribute('data-order-id')) as string

  // Routing cannot assign a pharmacy here (no routing licence is recordable through a served route): the refusal is recorded,
  // fails closed, and is not shown as a route
  const route = await page.request.post(`${API}/api/orders/${orderId}/route`, { data: { latitude: 24.7136, longitude: 46.6753 } })
  expect(route.status()).toBe(409)
  const refusal = (await route.json()).detail
  expect(refusal.error).toBe('NO_QUALIFYING_PHARMACY')
  expect(refusal.decision.chosen_location_id).toBeNull()
  await page.reload()
  await page.waitForLoadState('networkidle')
  await expectSteps(order, { PLACED: true, ROUTED: false, DELIVERED: false, RECEIPT_ISSUED: false })

  // The licensed pharmacy delivers and confirms the cash: delivered and receipt issued, in that order
  const delivered = await clinic.post(`/api/orders/${orderId}/deliver`, { data: { location_id: locationId,
    batches: { [GENERAL]: batch }, collected_amount_halalas: 1500, collection_reference: `COD-${tag}` } })
  expect(delivered.status(), await delivered.text()).toBe(200)
  await clinic.dispose()
  await page.reload()
  await page.waitForLoadState('networkidle')
  await expectSteps(order, { PLACED: true, ROUTED: false, DELIVERED: true, RECEIPT_ISSUED: true })
  await expect(order).toHaveAttribute('data-status', 'DELIVERED')
  await expect(order.getByTestId('receipt')).toBeVisible()
  await expect(tracking).not.toContainText(/carrier|courier ETA|in transit/i)
  if (lang === 'ar') expect(await untranslated(page, 'main')).toEqual([])

  // The API view agrees with the page and carries no carrier data
  const view = (await (await page.request.get(`${API}/api/orders`)).json()).find((o: { order_id: string }) => o.order_id === orderId)
  expect(view.tracking.carrier).toBeNull()
  expect(view.tracking.steps.map((s: { step: string; done: boolean }) => [s.step, s.done]))
    .toEqual([['PLACED', true], ['ROUTED', false], ['DELIVERED', true], ['RECEIPT_ISSUED', true]])
})
