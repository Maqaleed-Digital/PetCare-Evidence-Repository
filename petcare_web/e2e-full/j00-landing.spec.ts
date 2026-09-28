/** J-00 — public landing (MVC-EPC-D-001 D2). Full stack; Arabic default for a new visitor; English alternate. */
import { test, expect, untranslated } from './fixtures'

test('[J-00] @S:PUB-01 landing: Arabic by default, owner and veterinarian entry points, PDPL notice', async ({ page, lang }) => {
  await page.goto('/')
  await page.waitForLoadState('networkidle')
  await expect(page.locator('html')).toHaveAttribute('dir', lang === 'ar' ? 'rtl' : 'ltr')
  await expect(page.getByTestId('entry-owner')).toBeVisible()
  await expect(page.getByTestId('entry-vet')).toBeVisible()
  await expect(page.getByTestId('cta-register')).toHaveAttribute('href', '/signup')
  const pdpl = page.getByTestId('pdpl-notice')
  await expect(pdpl).toBeVisible()
  await expect(pdpl.locator('a[href="/privacy"]')).toBeVisible()
  if (lang === 'ar') expect(await untranslated(page)).toEqual([])        // X1: no English-only text in Arabic mode
})
