/**
 * PORT-04 / PORT-05 / PORT-06 — viewport, safety reachability, crash detection.
 *
 * Ported behaviour from the validated petcare-platform harness, re-expressed for
 * this app. It extends the existing Playwright configuration rather than adding
 * a second harness: the port source keeps its harness in a separate npm package
 * only because that repository has an unrelated peer-dependency conflict, and
 * that reason does not exist here.
 *
 *   PORT-04  seven viewports across the canonical routes
 *   PORT-05  safety-critical controls reachable at 320 px
 *   PORT-06  no page raises an unhandled render error
 *
 * These assert measurable layout facts, not aesthetics. Human visual acceptance
 * (MVC-UX-03) remains a separate act and is not claimed by anything here.
 *
 * Authority: MVC-GOV-CANON-001 (controlled port from LEGACY_TO_PORT_FROM).
 */
import { test, expect, type Page } from '@playwright/test'

/** PORT-04: the seven viewport classes carried over from the validated source. */
const VIEWPORTS = [
  { name: '320x568', width: 320, height: 568 },
  { name: '375x667', width: 375, height: 667 },
  { name: '390x844', width: 390, height: 844 },
  { name: '430x932', width: 430, height: 932 },
  { name: '768x1024', width: 768, height: 1024 },
  { name: '1280x800', width: 1280, height: 800 },
  { name: '1440x900', width: 1440, height: 900 },
]

/** Routes this app actually serves, read from app/. */
const ROUTES = [
  { path: '/', label: 'landing', critical: false },
  { path: '/register', label: 'register', critical: false },
  { path: '/signin', label: 'signin', critical: false },
  { path: '/owner', label: 'owner', critical: false },
  { path: '/owner/emergency', label: 'owner emergency', critical: true },
  { path: '/vet', label: 'vet', critical: true },
  { path: '/pharmacy', label: 'pharmacy', critical: true },
  { path: '/admin', label: 'admin', critical: false },
  { path: '/account', label: 'account', critical: false },
  { path: '/privacy', label: 'privacy', critical: false },
  { path: '/unauthorized', label: 'unauthorized', critical: false },
]

/**
 * Answer identity so role surfaces render, and hand back empty collections for
 * everything else so each page shows its real empty state rather than crashing.
 * A layout assertion on an empty state is still a layout assertion.
 */
async function stubApi(page: Page, role = 'owner') {
  await page.route('**/api/**', async (route) => {
    const url = route.request().url()
    if (url.includes('/auth/me') || url.includes('/auth/session')) {
      return route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          user_id: 'u-viewport',
          email: 'viewport@example.test',
          full_name: 'Viewport',
          role,
        }),
      })
    }
    return route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([]),
    })
  })
}

/** Horizontal overflow of the document itself, in CSS pixels. */
async function horizontalOverflow(page: Page): Promise<number> {
  return page.evaluate(() => {
    const d = document.documentElement
    return Math.max(
      0,
      Math.max(d.scrollWidth, document.body.scrollWidth) - d.clientWidth,
    )
  })
}

// ---------------------------------------------------------------------------
// PORT-04 — viewport breadth
// ---------------------------------------------------------------------------

test.describe('PORT-04 viewport breadth', () => {
  for (const route of ROUTES) {
    for (const vp of VIEWPORTS) {
      test(`${route.label} holds its layout at ${vp.name}`, async ({ page }) => {
        const crashes: string[] = []
        page.on('pageerror', (e) => crashes.push(String(e)))

        await page.setViewportSize({ width: vp.width, height: vp.height })
        await stubApi(page)
        await page.goto(route.path)

        // Something rendered: React mounted and produced children. A visibility
        // assertion on <body> is the wrong instrument -- a fixed-position layout
        // leaves body with a zero-height box, which reads as "hidden".
        await expect
          .poll(() => page.evaluate(() => document.body.children.length))
          .toBeGreaterThan(0)

        expect(
          await horizontalOverflow(page),
          `${route.label} overflows horizontally at ${vp.name}`,
        ).toBe(0)

        // PORT-06 rides along: a crash on any route at any viewport fails here.
        expect(
          crashes,
          `${route.label} raised a page error at ${vp.name}`,
        ).toEqual([])
      })
    }
  }
})

// ---------------------------------------------------------------------------
// Arabic-first document defaults, at every viewport
// ---------------------------------------------------------------------------

test.describe('Arabic-first defaults survive every viewport', () => {
  for (const vp of VIEWPORTS) {
    test(`lang=ar and dir=rtl at ${vp.name}`, async ({ page }) => {
      await page.setViewportSize({ width: vp.width, height: vp.height })
      await stubApi(page)
      await page.goto('/')
      await expect(page.locator('html')).toHaveAttribute('lang', 'ar')
      await expect(page.locator('html')).toHaveAttribute('dir', 'rtl')
    })
  }
})

// ---------------------------------------------------------------------------
// PORT-05 — safety-critical reachability at 320 px
// ---------------------------------------------------------------------------

test.describe('PORT-05 safety-critical controls at 320px', () => {
  const NARROW = { width: 320, height: 568 }

  for (const route of ROUTES.filter((r) => r.critical)) {
    test(`${route.label} keeps its controls inside a 320px viewport`, async ({
      page,
    }) => {
      await page.setViewportSize(NARROW)
      await stubApi(page, route.path.startsWith('/vet') ? 'veterinarian' : 'owner')
      await page.goto(route.path)

      expect(await horizontalOverflow(page)).toBe(0)

      // Scoped to <main> where the app provides it. A sidebar or drawer that is
      // off-canvas below its breakpoint is outside the viewport BY DESIGN, and
      // asserting over it measures the pattern rather than a defect -- the
      // false positive this check was corrected for in the source harness.
      const offscreen = await page.evaluate((w) => {
        const scope: ParentNode = document.querySelector('main') ?? document.body
        const bad: string[] = []
        for (const el of Array.from(
          scope.querySelectorAll('button, a[href], [role=button]'),
        )) {
          const r = el.getBoundingClientRect()
          if (r.width === 0 && r.height === 0) continue
          const style = window.getComputedStyle(el as Element)
          if (style.visibility === 'hidden' || style.display === 'none') continue
          if (r.left < -1 || r.right > w + 1) {
            bad.push(
              (el.textContent || el.getAttribute('aria-label') || el.tagName)
                .trim()
                .slice(0, 40),
            )
          }
        }
        return bad
      }, NARROW.width)

      expect(
        offscreen,
        `controls outside a 320px viewport on ${route.label}`,
      ).toEqual([])
    })
  }
})

// ---------------------------------------------------------------------------
// PORT-06 — the error boundary contains a render failure
// ---------------------------------------------------------------------------

test.describe('PORT-06 render failures are contained', () => {
  test('a route whose data fails still renders a page, not a blank screen', async ({
    page,
  }) => {
    // Every API call fails. The page must degrade, not white-screen: this is the
    // defect class the source harness caught, where an admin surface threw on an
    // unexpected payload and unmounted the whole tree.
    await page.route('**/api/**', (route) =>
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'induced failure' }),
      }),
    )

    await page.setViewportSize({ width: 375, height: 667 })
    await page.goto('/owner')

    await expect
      .poll(() => page.evaluate(() => document.body.innerText.trim().length))
      .toBeGreaterThan(0)
    expect(await horizontalOverflow(page)).toBe(0)
  })
})
