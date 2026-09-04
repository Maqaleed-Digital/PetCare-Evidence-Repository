/**
 * PORT-01 / PORT-02 — absence-guard discipline, ported from the validated
 * petcare-platform harness.
 *
 * The discipline being ported is this: assert the FORBIDDEN state, not only the
 * good one. A test that checks the right thing is present passes just as happily
 * when the wrong thing is present beside it. Each guard below names a state that
 * must not exist and fails if it appears.
 *
 *   PORT-01  structural absence guards (retired roles, unsafe sinks)
 *   PORT-02  Arabic-first absence guards (no untranslated or hard-coded strings
 *            on customer paths)
 *
 * Authority: MVC-GOV-CANON-001 (controlled port from LEGACY_TO_PORT_FROM).
 */
import { describe, it, expect } from 'vitest'
import { readFileSync, readdirSync, statSync } from 'node:fs'
import { join, relative } from 'node:path'
import { STRINGS } from '@/lib/strings'

const ROOT = process.cwd()
const SOURCE_DIRS = ['app', 'components', 'lib']

function walk(dir: string, acc: string[] = []): string[] {
  let entries: string[]
  try { entries = readdirSync(dir) } catch { return acc }
  for (const e of entries) {
    if (e === 'node_modules' || e.startsWith('.')) continue
    const p = join(dir, e)
    if (statSync(p).isDirectory()) walk(p, acc)
    else if (/\.(ts|tsx)$/.test(p)) acc.push(p)
  }
  return acc
}

const SOURCES = SOURCE_DIRS.flatMap((d) => walk(join(ROOT, d)))

// ---------------------------------------------------------------------------
// PORT-01 — structural absence guards
// ---------------------------------------------------------------------------

describe('PORT-01 absence guards', () => {
  it('has sources to scan (the guard is not vacuous)', () => {
    // Without this, every absence assertion below would pass on an empty set.
    expect(SOURCES.length).toBeGreaterThan(20)
  })

  it('does not reintroduce the retired pharmacy_operator role', () => {
    // W0-D retires pharmacy_operator and fails dispensing closed to the
    // veterinarian. The port source still carries it as a first-class role, so
    // any tranche that copies its role model would silently reverse a security
    // decision. This guard makes that reversal loud.
    const offenders = SOURCES.filter((f) =>
      readFileSync(f, 'utf8').includes('pharmacy_operator'),
    ).map((f) => relative(ROOT, f))
    expect(offenders).toEqual([])
  })

  it('renders no unsanitised HTML sink on any surface', () => {
    const offenders = SOURCES.filter((f) =>
      readFileSync(f, 'utf8').includes('dangerouslySetInnerHTML'),
    ).map((f) => relative(ROOT, f))
    expect(offenders).toEqual([])
  })
})

// ---------------------------------------------------------------------------
// PORT-02 — Arabic-first absence guards
// ---------------------------------------------------------------------------

type Leaf = { path: string; ar: unknown; en: unknown }

function leaves(node: unknown, path: string[] = [], acc: Leaf[] = []): Leaf[] {
  if (node && typeof node === 'object') {
    const o = node as Record<string, unknown>
    if ('ar' in o || 'en' in o) {
      acc.push({ path: path.join('.'), ar: o.ar, en: o.en })
      return acc
    }
    for (const [k, v] of Object.entries(o)) leaves(v, [...path, k], acc)
  }
  return acc
}

const LEAVES = leaves(STRINGS)
const ARABIC = /[؀-ۿ]/

/**
 * Latin brand tokens that are deliberately identical in both languages.
 * Named one by one so the exemption cannot quietly widen, and constrained
 * below: an entry only earns the exemption if ar and en are byte-identical,
 * which a real untranslated string never is.
 */
const BRAND_EXEMPT = new Set(['nav.brand', 'signin.kicker', 'register.kicker'])

describe('PORT-02 Arabic-first absence guards', () => {
  it('found translatable strings to check (the guard is not vacuous)', () => {
    expect(LEAVES.length).toBeGreaterThan(10)
  })

  it('leaves no string half-translated', () => {
    const bad = LEAVES.filter(
      (l) =>
        typeof l.ar !== 'string' ||
        typeof l.en !== 'string' ||
        !(l.ar as string).trim() ||
        !(l.en as string).trim(),
    ).map((l) => l.path)
    expect(bad).toEqual([])
  })

  it('leaves no Arabic slot holding Latin placeholder text', () => {
    // The failure this catches is an `ar` value that was never translated and
    // still carries the English copy. Brand names are exempt by name, not by
    // guesswork, so the exemption cannot quietly widen.
    const bad = LEAVES.filter(
      (l) =>
        !BRAND_EXEMPT.has(l.path) &&
        typeof l.ar === 'string' &&
        !ARABIC.test(l.ar as string),
    ).map((l) => l.path)
    expect(bad).toEqual([])
  })

  it('lets nothing hide behind the brand exemption', () => {
    // A brand token reads the same in both languages. Anything on the exempt
    // list whose ar and en differ is not a brand -- it is an untranslated
    // string that has been given a pass, so the exemption itself is guarded.
    const notBrands = [...BRAND_EXEMPT].filter((path) => {
      const leaf = LEAVES.find((l) => l.path === path)
      return !leaf || leaf.ar !== leaf.en
    })
    expect(notBrands).toEqual([])
  })

  it('keeps Arabic the default language and RTL the default direction', () => {
    const provider = readFileSync(
      join(ROOT, 'components/LangProvider.tsx'),
      'utf8',
    )
    expect(provider).toMatch(/useState<Lang>\('ar'\)/)
    expect(provider).not.toMatch(/useState<Lang>\('en'\)/)
  })

  it('routes customer-facing nav copy through the string registry, not literals', () => {
    // Nav is the surface every customer path renders. A literal here is a
    // string the language toggle cannot reach.
    const nav = readFileSync(join(ROOT, 'components/Nav.tsx'), 'utf8')
    const jsxText = [...nav.matchAll(/>\s*([A-Za-z][A-Za-z ']{3,})\s*</g)].map(
      (m) => m[1].trim(),
    )
    expect(jsxText).toEqual([])
  })
})
