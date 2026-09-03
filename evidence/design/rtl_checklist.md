# P04 — Arabic RTL Checklist

## index.html

- [x] `<html lang="ar" dir="rtl">` — set as default
- [x] `<title>VetiCare — الرعاية البيطرية</title>`
- [x] DM Serif Display + DM Sans Google Fonts loaded via `<link>` in `<head>`

## index.css

- [x] CSS custom properties defined: `--font-heading`, `--font-body`, all `--vc-*` color tokens
- [x] `body { font-family: var(--font-body), … }` — DM Sans as primary
- [x] `h1–h6 { font-family: var(--font-heading), … }` — DM Serif Display for headings
- [x] `[dir="rtl"]` rules defined for RTL font fallbacks

## tailwind.config.js

- [x] `fontFamily.heading` and `fontFamily.body` added
- [x] VetiCare brand color tokens added: `vc-primary`, `vc-secondary`, `vc-background`, `vc-surface`, `vc-text`, `vc-text-muted`, `vc-danger`, `vc-warning`, `vc-success`

## i18n

- [x] `i18next` + `react-i18next` installed
- [x] `src/locales/ar.json` — complete Arabic translations (primary)
- [x] `src/locales/en.json` — complete English translations (fallback)
- [x] `src/i18n.js` — configured with `lng: 'ar'`, `fallbackLng: 'en'`
- [x] `App.js` imports `./i18n` at root

## PetCare → VetiCare brand fixes

| File | Change |
|------|--------|
| `src/pages/SignIn.jsx` | Brand name → `t("brand.name")` (renders "VetiCare") |
| `src/components/Layout.jsx` line 71 | "PetCare" → "VetiCare" |
| `src/components/Layout.jsx` line 127 | "PetCare Standalone" → "VetiCare" |

## Remaining PetCare references (non-breaking — human to review)

| File | Line | Content |
|------|------|---------|
| `src/pages/Report.jsx` | 77 | Download filename — "PetCare_Sprint6…" |
| `src/pages/Report.jsx` | 95, 217 | Descriptive text |
| `src/pages/Dashboard.jsx` | 278 | Descriptive text |
| `src/pages/SprintClosurePack.jsx` | 102 | Sprint description text |

These are data/content references, not brand-identity elements. Programme governor to decide if sprint content files need updating.

## Icon system

- [x] `src/components/Icon.jsx` created with 5 icons: paw, stethoscope, pill, shield, alert-circle
- [x] All icons are 24×24 viewBox SVG, line-icon style, `currentColor` stroke

## Arabic content verified on pages

- [x] SignIn — title, subtitle, labels, buttons use `t()` keys
- [ ] Dashboard — uses English static strings (no `t()` calls yet — out of scope for P04 unless explicitly instructed)
- [ ] Evidence, Security, Report — same (P04 scope was sign-in + landing + onboarding + unauthorized)
