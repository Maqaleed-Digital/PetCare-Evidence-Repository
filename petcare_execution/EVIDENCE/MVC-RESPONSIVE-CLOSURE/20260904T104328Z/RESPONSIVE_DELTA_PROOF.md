# Responsive delta proof — red → green

Same harness, same assertions, same file. Nothing in `e2e/` was touched.

```
BEFORE   PLAYWRIGHT_TOTAL=90  PASS=53  FAIL=37
AFTER    PLAYWRIGHT_TOTAL=90  PASS=90  FAIL=0

ASSERTIONS_WEAKENED = 0
NEW_REGRESSIONS     = 0
FILES_CHANGED       = 1   (petcare_web/app/globals.css)
E2E_SPECS_CHANGED   = 0
```

## The change

All 37 failures had one cause, so there is one fix. `.nav` was a single
non-wrapping flex row needing 407px; below 430px its content was pushed outside
the viewport and clipped by the blanket `html, body { overflow-x: hidden }`.

| Change | Why |
|---|---|
| `.nav { flex-wrap: wrap; row-gap: 8px }` | the bar wraps instead of overflowing — the root-cause fix |
| `.nav { height → min-height: 56px }` | a fixed height clips the second row once it wraps |
| `.nav-links`, `.nav-actions` — `flex-wrap: wrap`, `min-width: 0` | flex children default to `min-width:auto` and refuse to shrink below content |
| `margin-right → margin-inline-end` (brand), `margin-left → margin-inline-start` (actions) | this app renders `dir="rtl"` by default, where the physical properties are inverted — the spacing was being applied to the wrong side in the primary language |
| `@media (max-width:640px)` — `.nav { padding: 8px 16px }`, `.nav-actions { margin-inline-start: 0 }` | vertical breathing room for the wrapped row |

Measured effect on `/` at 320px: `nav.scrollWidth 407 → 320`, `body.scrollWidth
407 → 320`, `overflow 87px → 0`.

## What was deliberately not done

**No assertion was relaxed.** `horizontalOverflow(page) === 0` is unchanged, and
the e2e directory has no diff.

**No new `overflow-x: hidden` was added.** The existing blanket rule at
`globals.css:275` was left in place but is now load-bearing on nothing — the
content fits. It is recorded below as a residual, not treated as a fix.

**The nav items are now reachable.** PORT-05 asks whether safety-critical
controls sit inside a 320px viewport on the emergency, vet and pharmacy routes.
It failed before because the controls were clipped out of reach, not because they
were missing. It passes now because they wrap into view.

## Residual recorded, not fixed here

`html, body { overflow-x: hidden }` (`globals.css:275`, from MVC-UX-WO-001 WI-2)
is a blanket rule that will visually mask any future overflow from a human while
the tests keep catching it. Removing it is a separate change with its own
regression surface and is not bundled into a responsive fix. Recorded as
`BLANKET_OVERFLOW_X_HIDDEN_RESIDUAL`.

## Regression sweep

```
Playwright        90 / 90 pass
vitest            76 / 76 pass (15 files)
petcare_api       46 / 46 pass
tsc --noEmit      clean, exit 0
next build        PASS — all 14 routes built
next lint         NOT_CONFIGURED — `next lint` drops into interactive ESLint
                  setup; no lint result is claimed either way
```
