/**
 * J-O1 — owner self-registration, email verification (FAKE email adapter), sign in, sign out, password reset.
 * Full stack: browser -> petcare_web -> main:app -> PostgreSQL. Self-registration is ON in this stack (Sponsor ruling 1:
 * production default OFF; the OFF state is proven by the served-app tests).
 */
import { test, expect, dismissFirstRun, lastEmailLink, signIn, untranslated } from './fixtures'

const API = process.env.PETCARE_E2E_API ?? 'http://localhost:8090'
const PW1 = 'Owner-passw0rd-1'
const PW2 = 'Owner-passw0rd-2'

test('[J-O1] @S:PUB-07 an owner self-registers, verifies the email, signs in and out, and resets the password', async ({ page, lang }, info) => {
  const email = `owner.${info.project.name}.${Date.now()}@e2e.test`
  await page.goto('/signup')
  await page.waitForLoadState('networkidle')
  const form = page.getByTestId('self-register-form')
  await expect(form).toBeVisible()
  if (lang === 'ar') expect(await untranslated(page)).toEqual([])
  await form.locator('input[autocomplete="name"]').fill(lang === 'ar' ? 'مالك تجريبي' : 'Test Owner')
  await form.locator('input[type="email"]').fill(email)
  await form.locator('input[type="password"]').fill(PW1)
  // D2d (R13.3): care reminders are offered as a separate, optional choice, unticked by default.
  const reminders = form.getByTestId('self-register-care-reminders')
  await expect(reminders).toBeVisible()
  await expect(reminders).not.toBeChecked()
  expect(await reminders.getAttribute('required')).toBeNull()
  await form.getByTestId('self-register-privacy').check()
  await form.locator('button[type="submit"]').click()
  await expect(page.getByTestId('self-register-sent')).toBeVisible()

  await signIn(page, email, PW1)                                               // not yet verified: refused
  await expect(page).toHaveURL(/\/signin/)
  await expect(page.getByRole('alert').first()).toBeVisible()

  await page.goto(await lastEmailLink(email, 'EMAIL_VERIFICATION'))
  await expect(page.getByTestId('verify-ok')).toBeVisible()

  await signIn(page, email, PW1)
  await expect(page).toHaveURL(/\/owner/)
  await page.waitForLoadState('networkidle')
  await dismissFirstRun(page)
  if (lang === 'ar') expect(await untranslated(page, 'nav')).toEqual([])      // X1: the signed-in navigation too
  await page.getByRole('button', { name: lang === 'ar' ? 'تسجيل الخروج' : 'Sign out' }).click()
  await expect.poll(async () => page.evaluate(async (api) =>
    (await fetch(`${api}/api/auth/me`, { credentials: 'include' })).status, API)).toBe(401)

  await page.goto('/forgot-password')
  await page.waitForLoadState('networkidle')
  await page.locator('input[type="email"]').fill(email)
  await page.locator('form button[type="submit"]').click()
  await expect(page.getByTestId('forgot-sent')).toBeVisible()
  await page.goto(await lastEmailLink(email, 'PASSWORD_RESET'))
  await page.waitForLoadState('networkidle')
  await page.locator('input[type="password"]').fill(PW2)
  await page.locator('form button[type="submit"]').click()
  await expect(page.getByTestId('reset-done')).toBeVisible()

  await signIn(page, email, PW1)                                               // the old password no longer works
  await expect(page).toHaveURL(/\/signin/)
  await signIn(page, email, PW2)
  await expect(page).toHaveURL(/\/owner/)
})
