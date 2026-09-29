/**
 * J-O4 — an owner adds a pet, opens its profile and history, and edits its care preferences (CO-02 household and
 * pets, CO-03 pet profile and timeline). Full stack; the page is the FR-02 screen (its unit test is registered FR-02
 * evidence and is not touched here).
 */
import { test, expect, newOwner, untranslated } from './fixtures'

test('[J-O4] @S:CO-02 @S:CO-03 an owner adds a pet, opens its profile and history, and edits care preferences', async ({ page, lang }, info) => {
  await newOwner(page, info, 'jo4', lang)
  await page.goto('/owner/pets')
  await page.waitForLoadState('networkidle')
  const name = lang === 'ar' ? 'لونا' : 'Luna'
  const species = lang === 'ar' ? 'قطة' : 'cat'
  const form = page.locator('form').filter({ has: page.locator('input[name="species"]') })
  await form.locator('input[name="name"]').fill(name)
  await form.locator('input[name="species"]').fill(species)
  await form.locator('input[name="birth_date"]').fill('2023-04-01')
  await form.locator('input[name="weight_kg"]').fill('4.2')
  await form.locator('input[name="allergies"]').fill(lang === 'ar' ? 'لا شيء' : 'none known')
  await form.locator('button[type="submit"]').click()

  const entry = page.getByRole('button', { name: `${name} · ${species}` })
  await expect(entry).toBeVisible()
  await entry.click()
  const profile = page.getByRole('region', { name })
  await expect(profile.getByRole('heading', { name })).toBeVisible()
  await expect(profile.locator('dd').first()).toHaveText(species)
  if (lang === 'ar') expect(await untranslated(page, 'main')).toEqual([])

  const prefs = lang === 'ar' ? 'تفضّل الطعام الرطب' : 'Prefers wet food'
  await profile.locator('textarea').fill(prefs)
  await profile.getByRole('button').last().click()

  await page.reload()                                                         // the server kept it, not the tab
  await page.waitForLoadState('networkidle')
  await page.getByRole('button', { name: `${name} · ${species}` }).click()
  await expect(page.getByRole('region', { name }).locator('textarea')).toHaveValue(prefs)
})
