/**
 * J-O2 consent · J-O3 profile + personal-data export (SQ-3 #11) · J-O11 owner MFA — the account centre (CO-15).
 * Full stack: browser -> petcare_web -> main:app -> PostgreSQL. Step-up is ENFORCED by the served app in this stack; the
 * journey plays the owner's authenticator app (fixtures.totp). Each journey registers its own owner (J-O1 path).
 */
import { Page } from '@playwright/test'
import { test, expect, newOwner, totp, untranslated } from './fixtures'

/** Enrol TOTP at /account/security; returns the Base32 key and the one-time recovery codes. */
async function enrolMfa(page: Page, password: string): Promise<{ key: string; codes: string[] }> {
  await page.goto('/account/security')
  await page.waitForLoadState('networkidle')
  await page.getByTestId('mfa-start').click()
  const reauth = page.getByTestId('mfa-reauth')                     // no factor yet: SQ-3 asks for the password instead
  await expect(reauth).toBeVisible()
  await reauth.locator('input[type="password"]').fill(password)
  await reauth.locator('button[type="submit"]').click()
  const key = (await page.getByTestId('mfa-key').innerText()).trim()
  expect(key).toMatch(/^[A-Z2-7]{16,}$/)
  await page.getByTestId('mfa-confirm').locator('#mfa-code').fill(await totp(key))
  await page.getByTestId('mfa-confirm').locator('button[type="submit"]').click()
  const list = page.getByTestId('mfa-code-list')
  await expect(list).toBeVisible()
  const codes = (await list.locator('li').allInnerTexts()).map(c => c.trim())
  await page.getByTestId('mfa-codes-saved').click()
  await expect(page.getByTestId('mfa-done')).toBeVisible()
  return { key, codes }
}

test('[J-O2] @S:CO-15 an owner reviews, grants and withdraws consent, and the history is kept on the server', async ({ page, lang }, info) => {
  await newOwner(page, info, 'jo2', lang)
  await page.goto('/account')
  await page.waitForLoadState('networkidle')
  const ledger = page.getByTestId('consent-ledger')
  await expect(ledger.getByTestId('consent-privacy_notice')).toHaveAttribute('data-granted', 'true')   // from sign-up
  await expect(ledger.getByTestId('consent-privacy_notice').getByRole('button')).toHaveCount(0)       // not a toggle
  if (lang === 'ar') expect(await untranslated(page, 'main')).toEqual([])

  const reminders = ledger.getByTestId('consent-care_reminders')
  await expect(reminders).toHaveAttribute('data-granted', 'false')
  await ledger.getByTestId('consent-care_reminders-grant').click()
  await expect(reminders).toHaveAttribute('data-granted', 'true')
  await ledger.getByTestId('consent-care_reminders-revoke').click()
  await expect(reminders).toHaveAttribute('data-granted', 'false')

  await page.reload()                                                         // the state is the server's, not the tab's
  await page.waitForLoadState('networkidle')
  await expect(page.getByTestId('consent-care_reminders')).toHaveAttribute('data-granted', 'false')
  const history = page.getByTestId('consent-history')
  await history.locator('summary').click()
  await expect(history.locator('li')).toHaveCount(3)                          // sign-up grant + grant + withdrawal
})

test('[J-O3] @S:CO-15 an owner edits their name and downloads their personal data after step-up', async ({ page, lang }, info) => {
  const { email, password } = await newOwner(page, info, 'jo3', lang)
  await page.goto('/account')
  await page.waitForLoadState('networkidle')
  const form = page.getByTestId('profile-form')
  await expect(form.getByTestId('profile-email')).toHaveText(email)
  const name = lang === 'ar' ? 'نورة العتيبي' : 'Noura Alotaibi'
  await form.locator('input[name="full_name"]').fill(name)
  await form.locator('button[type="submit"]').click()
  await expect(page.getByTestId('profile-saved')).toBeVisible()
  await page.reload()
  await page.waitForLoadState('networkidle')
  await expect(page.getByTestId('profile-form').locator('input[name="full_name"]')).toHaveValue(name)

  await page.getByTestId('data-export-download').click()                     // no factor yet: the server refuses
  await expect(page.getByTestId('enrolment-required')).toBeVisible()

  const { key } = await enrolMfa(page, password)
  await page.goto('/account')
  await page.waitForLoadState('networkidle')
  const downloading = page.waitForEvent('download')
  await page.getByTestId('data-export-download').click()
  const dialog = page.getByTestId('step-up-dialog')
  await expect(dialog).toBeVisible()
  await dialog.locator('#step-up-code').fill(await totp(key, Date.now() + 30_000))   // the next step: never a replay
  await dialog.locator('button[type="submit"]').click()
  const file = await (await downloading).path()
  await expect(page.getByTestId('data-export-done')).toBeVisible()
  const fs = await import('node:fs')
  const raw = fs.readFileSync(file, 'utf8')
  const body = JSON.parse(raw)
  expect(body.format).toBe('myveticare.personal-data-export.v1')
  expect(body.identity.email).toBe(email)
  expect(body.identity.full_name).toBe(name)
  expect(body.consents.map((c: { purpose: string }) => c.purpose)).toContain('privacy_notice')
  for (const secret of ['password', 'otpauth', 'recovery', key]) expect(raw.toLowerCase()).not.toContain(secret.toLowerCase())
})

test('[J-O11] @S:CO-15 an owner enrols two-step verification and a recovery code works exactly once', async ({ page, lang }, info) => {
  const { password } = await newOwner(page, info, 'jo11', lang)
  const { codes } = await enrolMfa(page, password)
  expect(codes).toHaveLength(10)
  if (lang === 'ar') expect(await untranslated(page, 'main')).toEqual([])
  await page.reload()                                                         // shown once: never re-displayed
  await page.waitForLoadState('networkidle')
  await expect(page.getByTestId('mfa-code-list')).toHaveCount(0)

  await page.goto('/account')
  await page.waitForLoadState('networkidle')
  const downloading = page.waitForEvent('download')
  await page.getByTestId('data-export-download').click()
  const dialog = page.getByTestId('step-up-dialog')
  await dialog.getByRole('button', { name: lang === 'ar' ? 'استخدام رمز استرداد بدلاً من ذلك' : 'Use a recovery code instead' }).click()
  await dialog.locator('#step-up-code').fill(codes[0])
  await dialog.locator('button[type="submit"]').click()
  await downloading
  await expect(page.getByTestId('data-export-done')).toBeVisible()

  const reused = await page.evaluate(async ([api, code]) => (await fetch(`${api}/api/me/mfa/recovery`, {
    method: 'POST', credentials: 'include', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ code }),
  })).status, [process.env.PETCARE_E2E_API ?? 'http://localhost:8090', codes[0]] as const)
  expect(reused).toBe(401)                                                    // a recovery code is single use
})
