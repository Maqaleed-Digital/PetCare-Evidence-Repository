# Responsive red baseline — MEASURED, not relayed

**Measured 2026-09-04**, Playwright project `mobile-chromium`, canonical web tree
`petcare_web/`. Raw capture: `playwright_baseline_raw.txt`.

```
PLAYWRIGHT_TOTAL = 90
PLAYWRIGHT_PASS  = 53
PLAYWRIGHT_FAIL  = 37
```

## The relayed baseline was wrong on two of three numbers

The carried figure was `88/51/37`. Measured is **`90/53/37`**. The failure count
is exact; the total and pass were each understated by 2. The instruction not to
assume 51/37 earned itself — a static count of `test(` declarations gives 6, and
the real total only appears by running the suite, because the cases are generated
by nested loops.

Structure: 11 routes × 7 viewports = 77 (PORT-04), + 7 Arabic-defaults, + 3
PORT-05, + 1 PORT-06, + 2 pilot-path = **90**.

## All 37 failures are one defect

| Failing group | Count |
|---|---|
| PORT-04 at 320×568 | 11 (every route) |
| PORT-04 at 375×667 | 11 (every route) |
| PORT-04 at 390×844 | 11 (every route) |
| PORT-05 safety controls at 320px | 3 (owner emergency, vet, pharmacy) |
| PORT-06 error boundary at 375px | 1 |

Every route fails at 320/375/390 and passes at 430/768/1280/1440. Not eleven
route bugs — one shared component, and a single breakpoint.

All 37 assert the same thing: `horizontalOverflow(page) === 0`.

## Root cause

`<nav class="nav">` — `components/Nav.tsx`, rendered by the app layout on every
route — is a single non-wrapping flex row: brand, links, language toggle, and a
sign-in button.

```
at clientWidth 320:  nav.scrollWidth = 407   =>  body.scrollWidth = 407   =>  overflow = 87px
at clientWidth 430:  nav.scrollWidth = 430   =>  body.scrollWidth = 430   =>  overflow = 0
```

## Why nobody could see it

`app/globals.css:264` carries `html, body { overflow-x: hidden; }`, added under
MVC-UX-WO-001 WI-2. It made the symptom invisible without changing the fact:

- `documentElement.scrollWidth` reads 320, equal to `clientWidth`
- `window.scrollTo(9999, 0)` does not move — `windowCanScrollX = false`
- no element reports `right > 320`

So the page looks fine and cannot be scrolled sideways. **The nav items past
320px were not absent — they were clipped out of reach.** That is why PORT-05,
which asks whether safety-critical controls are reachable at 320px, fails on
exactly the three critical routes.

This is the blanket-`overflow-x:hidden` anti-pattern the port plan warns against,
already present in the tree before this lane.

## Why the guard still caught it

`scrollWidth` reports the scrollable overflow region **even when overflow is
hidden**. The assertion measured `body.scrollWidth` and saw 407 regardless of the
clipping. The guard was armed, not defeated — the blanket rule hid the defect
from a human, not from the test.
