# P04 — Brand Audit: PetCare → VetiCare

## Files changed

| File | Change type | Old value | New value |
|------|------------|-----------|-----------|
| `frontend/public/index.html` | Title | `Emergent \| Fullstack App` | `VetiCare — الرعاية البيطرية` |
| `frontend/public/index.html` | HTML lang | `lang="en"` | `lang="ar"` |
| `frontend/public/index.html` | HTML dir | (absent) | `dir="rtl"` |
| `frontend/src/pages/SignIn.jsx` | Brand name text | `"PetCare"` | `t("brand.name")` → "VetiCare" |
| `frontend/src/pages/SignIn.jsx` | Sign-in title | `"Pilot sign-in"` | `t("auth.sign_in_title")` |
| `frontend/src/pages/SignIn.jsx` | Form labels | `"Email"`, `"Password"` | `t("auth.email")`, `t("auth.password")` |
| `frontend/src/pages/SignIn.jsx` | Button text | `"Sign in"` | `t("auth.sign_in")` |
| `frontend/src/components/Layout.jsx:71` | Sidebar brand | `"PetCare"` | `"VetiCare"` |
| `frontend/src/components/Layout.jsx:127` | Footer label | `"PetCare Standalone"` | `"VetiCare"` |
| `frontend/tailwind.config.js` | Theme tokens | Generic tokens only | + VetiCare `vc-*` tokens |
| `frontend/src/index.css` | Fonts | Inter / Manrope | DM Sans / DM Serif Display (via CSS vars) |

## Files created

| File | Purpose |
|------|---------|
| `frontend/src/i18n.js` | i18next config — Arabic default, English fallback |
| `frontend/src/locales/ar.json` | Arabic translations (primary) |
| `frontend/src/locales/en.json` | English translations (fallback) |
| `frontend/src/components/Icon.jsx` | SVG icon system replacing emoji |
| `frontend/src/assets/icons/` | Directory for future SVG assets |

## Remaining "PetCare" occurrences not touched

These are in sprint/content data files, not brand-identity UI elements:
- `src/pages/Report.jsx` — download filename, descriptive content
- `src/pages/Dashboard.jsx` — descriptive text
- `src/pages/SprintClosurePack.jsx` — sprint metadata string

Programme Governor to confirm if these need updating.
