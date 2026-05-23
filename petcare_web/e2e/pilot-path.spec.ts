/**
 * Pilot-path Playwright smoke (MVC-UX-WO-001 Definition of Done):
 *   "A holder of a valid invite can register on a phone, in Arabic,
 *    complete a guided first-run to a first real action on the existing
 *    /owner portal, navigate in RTL, and reach an emergency entry point."
 *
 * Backend is mocked at the network layer via page.route() so the smoke
 * does not require petcare_api to be running. Runs against a Pixel 7
 * mobile viewport (configured in playwright.config.ts) so the phone-
 * width reflow + 48 px touch invariants are exercised end-to-end.
 */
import { test, expect } from '@playwright/test'

const VALID_INVITE = 'OWNER-PILOT-001'

test.beforeEach(async ({ page }) => {
  // Mock POST /api/auth/register — happy path.
  await page.route('**/api/auth/register', async (route) => {
    const body = JSON.parse(route.request().postData() ?? '{}')
    await route.fulfill({
      status: 201,
      contentType: 'application/json',
      body: JSON.stringify({
        user: {
          user_id:   'u-smoke-1',
          email:     body.email,
          full_name: body.name,
          role:      body.role,
        },
      }),
    })
  })
})

test('register → first-run → /owner → emergency, in Arabic / RTL, on a phone viewport', async ({ page }) => {
  // Step 1 — land on /register (Arabic-first by default)
  await page.goto('/register')

  // RTL assertion (the headline pilot-mobile invariant)
  await expect(page.locator('html')).toHaveAttribute('dir', 'rtl')
  await expect(page.locator('html')).toHaveAttribute('lang', 'ar')

  // Arabic register surface visible (invite-only badge + AR title)
  await expect(page.getByText(/دعوة فقط — مرحلة التجريب/)).toBeVisible()
  await expect(page.getByText(/إنشاء حساب التجريب/)).toBeVisible()

  // Step 2 — submit a valid invite
  await page.getByLabel(/الاسم الكامل/).fill('مالك التجريب')
  await page.getByLabel(/البريد الإلكتروني/).fill('pilot-owner@example.com')
  await page.getByLabel(/رمز الدعوة/).fill(VALID_INVITE)
  await page.getByLabel(/كلمة المرور/).fill('Pilot2026!')
  await page.getByRole('button', { name: /إنشاء الحساب/ }).click()

  // Step 3 — owner portal (role cookie set client-side; middleware allows /owner)
  await page.waitForURL('**/owner')
  await expect(page.getByText('بوابة المالك')).toBeVisible()
  await expect(page.locator('html')).toHaveAttribute('dir', 'rtl')

  // Step 4 — first-run modal appears on first /owner visit
  const dialog = page.getByRole('dialog')
  await expect(dialog).toBeVisible()
  await expect(dialog.getByText(/مرحباً بك في VetiCare/)).toBeVisible()

  // Step through to the emergency-pointer step and finish
  await dialog.getByRole('button', { name: /التالي/ }).click()
  await dialog.getByRole('button', { name: /التالي/ }).click()
  await expect(dialog.getByText(/في الطوارئ، اضغط زر الحالة الطارئة/)).toBeVisible()
  await dialog.getByRole('link', { name: /إضافة أول حيوان أليف/ }).click()

  // Modal dismissed; /owner is the meaningful action surface
  await expect(page.getByRole('dialog')).not.toBeVisible()
  await expect(page.getByText('حيواناتي الأليفة')).toBeVisible()

  // Step 5 — emergency entry is reachable from /owner in 1 tap
  await page.getByRole('link', { name: /حالة طارئة/ }).click()
  await page.waitForURL('**/owner/emergency')
  await expect(page.getByText(/إرشادات فورية/)).toBeVisible()
  await expect(page.getByText(/جهة الاتصال للطوارئ/)).toBeVisible()
  // No-queue disclosure must be visible
  await expect(page.getByText(/لا يتم توجيه الحالات تلقائياً/)).toBeVisible()
  // Still RTL after navigation (toggle / lang persists across pages)
  await expect(page.locator('html')).toHaveAttribute('dir', 'rtl')
})
