/**
 * J-O8 — cash-on-delivery path (MVC-EPC-D-001 D2m; Sponsor ruling R19.5 item 3). Full stack: browser -> petcare_web -> main:app
 * -> PostgreSQL; no MyVetiCare API is mocked and no payment provider is involved.
 *
 * An owner opens the shop from their home, sees a GENERAL product and never the POM one, orders with cash on delivery, and —
 * once the supplying location is licensed (X-30, R19.1/R19.2 record) and the pharmacy confirms the collected cash — reads the
 * delivered order and its digital receipt. Staff steps (stock, licence, delivery) run through their own API sessions: there is
 * no staff orders screen yet (PH-02 / PH-14 / PH-16 are not built).
 *
 * Tagged [J-O8-COD], NOT [J-O8]: J-O8 also requires online payment, which is BLOCKED on X-05 / HyperPay (R18.4). Whether the COD
 * path alone counts J-O8 is a Sponsor ruling; until then report.mjs does not count it.
 */
import { request as pwRequest, APIRequestContext } from '@playwright/test'
import { test, expect, newOwner, dismissFirstRun, untranslated, USERS, SEED_PASSWORD } from './fixtures'

const API = process.env.PETCARE_E2E_API ?? 'http://localhost:8090'
const GENERAL = 'e2e-shampoo'          // seeded by tools/e2e_stack.py (synthetic registration)
const POM = 'e2e-amoxicillin'

async function staff(email: string): Promise<APIRequestContext> {
  const probe = await pwRequest.newContext({ baseURL: API })
  const r = await probe.post('/api/auth/sign-in', { data: { email, password: SEED_PASSWORD } })
  expect(r.status(), await r.text()).toBe(200)
  const cookie = r.headersArray().filter(h => h.name.toLowerCase() === 'set-cookie')
    .map(h => h.value.split(';')[0]).find(v => v.startsWith('petcare_session='))
  await probe.dispose()
  return pwRequest.newContext({ baseURL: API, extraHTTPHeaders: { cookie: cookie as string } })
}

test('[J-O8-COD] an owner orders a GENERAL product with cash on delivery and reads the receipt once a licensed pharmacy delivers', async ({ page, lang }, info) => {
  const tag = `${info.project.name}-${Date.now()}`
  await newOwner(page, info, 'jo8', lang)
  const pref = await page.request.put(`${API}/api/me/preferences/language`, { data: { language: lang } })
  expect(pref.status(), await pref.text()).toBe(200)

  // The clinic prices both products and stocks a pharmacy location (served staff routes)
  const clinic = await staff(USERS.clinicAdmin)
  for (const [pid, price] of [[GENERAL, 1500], [POM, 4200]] as const)
    expect((await clinic.post('/api/catalog/prices', { data: { product_id: pid, unit_price_halalas: price } })).status()).toBe(200)
  const loc = await clinic.post('/api/inventory/locations', { data: { name: `E2E pharmacy ${tag}` } })
  expect(loc.status(), await loc.text()).toBe(200)
  const locationId = (await loc.json()).location_id as string
  const batch = `B-${tag}`
  const stock = await clinic.post('/api/inventory/movements', { data: { location_id: locationId, product_id: GENERAL, batch,
    quantity_delta: 10, reason: 'RECEIPT', batch_expiry: '2032-06-30' } })
  expect(stock.status(), await stock.text()).toBe(200)

  // The owner opens the shop from their home: the GENERAL product is offered, the POM one is not
  await page.goto('/owner')
  await page.waitForLoadState('networkidle')
  await dismissFirstRun(page)
  await page.getByTestId('owner-open-orders').click()
  await expect(page).toHaveURL(/\/owner\/orders$/)
  const item = page.locator(`[data-testid="catalog-item"][data-product-id="${GENERAL}"]`)
  await expect(item).toContainText('E2E Synthetic Shampoo')
  await expect(page.locator(`[data-testid="catalog-item"][data-product-id="${POM}"]`)).toHaveCount(0)
  await expect(page.getByTestId('restricted-notice')).toBeVisible()
  if (lang === 'ar') expect(await untranslated(page, 'main')).toEqual([])

  // ... and orders two with cash on delivery (the only payment method offered)
  await page.locator(`[name="qty-${GENERAL}"]`).fill('2')
  await expect(page.locator('input[name="payment_method"][value="COD"]')).toBeChecked()
  await expect(page.locator('input[name="payment_method"]')).toHaveCount(1)
  await page.locator('form button[type="submit"]').click()
  const order = page.getByTestId('order')
  await expect(order).toHaveCount(1)
  await expect(order).toHaveAttribute('data-status', 'PLACED')
  await expect(order.getByTestId('order-lines')).toContainText('E2E Synthetic Shampoo')
  await expect(order.getByTestId('receipt')).toHaveCount(0)
  if (lang === 'ar') expect(await untranslated(page, 'main')).toEqual([])
  const orderId = (await order.getAttribute('data-order-id')) as string

  // A POM product cannot be ordered even by calling the API directly
  const pom = await page.request.post(`${API}/api/orders`, { data: { payment_method: 'COD', lines: [{ product_id: POM, quantity: 1 }] } })
  expect(pom.status()).toBe(409)
  expect((await pom.json()).detail.error).toBe('PRESCRIPTION_PRODUCT_NOT_ORDERABLE')

  // Fail closed: the location holds no establishment licence yet, so the delivery is refused and nothing is collected
  const deliver = () => clinic.post(`/api/orders/${orderId}/deliver`, { data: { location_id: locationId, batches: { [GENERAL]: batch },
    collected_amount_halalas: 3000, collection_reference: `COD-${tag}` } })
  const refused = await deliver()
  expect(refused.status()).toBe(409)
  expect((await refused.json()).detail.error).toBe('ESTABLISHMENT_LICENCE_INVALID')

  // A platform administrator records the location's licence (R19.2 record; an attestation, not registry verification — X-33)
  const admin = await staff(USERS.platformAdmin)
  const lic = await admin.post('/api/admin/establishment-licences', { data: { location_id: locationId,
    licence_number: `SFDA-EST-${tag}`, issuing_authority: 'SFDA', expires_on: '2099-12-31',
    basis: 'synthetic E2E entity data (R18.2)', licence_type: 'PHARMACY_ESTABLISHMENT', scope: 'veterinary medicines retail',
    evidence_document_ref: `DOC-E2E-${tag}` } })
  expect(lic.status(), await lic.text()).toBe(201)
  expect((await lic.json()).registry_verified).toBe(false)
  await admin.dispose()

  // The pharmacy delivers and confirms the exact cash collected
  const delivered = await deliver()
  expect(delivered.status(), await delivered.text()).toBe(200)
  await clinic.dispose()

  // The owner sees the order delivered and paid, with the digital receipt in their language
  await page.reload()
  await page.waitForLoadState('networkidle')
  await expect(order).toHaveAttribute('data-status', 'DELIVERED')
  const receipt = order.getByTestId('receipt')
  await expect(receipt).toBeVisible()
  await expect(receipt).toHaveAttribute('lang', lang)
  await expect(receipt).toHaveAttribute('dir', lang === 'ar' ? 'rtl' : 'ltr')
  await expect(receipt).toContainText(lang === 'ar' ? 'الدفع عند الاستلام' : 'cash on delivery')
  await expect(receipt).toContainText('30.00')
  if (lang === 'ar') expect(await untranslated(page, 'main')).toEqual([])
  const stored = await page.request.get(`${API}/api/orders/${orderId}/receipt`)
  expect(stored.status()).toBe(200)
  expect((await stored.json()).total_halalas).toBe(3000)
})
