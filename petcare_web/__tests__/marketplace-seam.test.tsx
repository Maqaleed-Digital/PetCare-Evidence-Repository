/**
 * PORT-09 — marketplace UI seam against the canonical partner_network services.
 *
 * The plan's constraint is four words: "must consume, never re-own". Both
 * halves need a guard, and they fail in opposite directions.
 *
 *   CONSUME    the seam must name reads that actually exist in
 *              petcare_runtime/src/petcare/partner_network/. A seam citing
 *              functions that were renamed or deleted looks identical to a
 *              wired one right up until it is wired.
 *
 *   NEVER      the web tree must contain no marketplace logic of its own. A
 *   RE-OWN     TypeScript copy of a pricing rule or a settlement transition
 *              becomes a second source of truth that drifts silently from the
 *              sealed Python one, and nothing fails when it does.
 *
 * EP-07 is sealed and MVC-GOV-CANON-001 lists `marketplace_activation` under
 * `does_not_authorize`, so the seam is deliberately unwired and fails closed.
 * The third group asserts that it fails closed *loudly* — no fabricated rows,
 * no empty list standing in for "no partners".
 *
 * Authority: MVC-GOV-CANON-001 (controlled port from LEGACY_TO_PORT_FROM).
 */
import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { readFileSync, readdirSync, statSync, existsSync } from 'node:fs'
import { join, resolve } from 'node:path'
import { LangProvider } from '@/components/LangProvider'
import { MarketplaceSeamPanel } from '@/components/MarketplaceSeamPanel'
import { CANONICAL_READS, MARKETPLACE_SEAM_WIRED, readMarketplace } from '@/lib/marketplace'
import AdminPage from '@/app/admin/page'

vi.mock('next/navigation', () => ({
  useRouter: () => ({ replace: vi.fn(), push: vi.fn() }),
  usePathname: () => '/admin',
}))

const WEB_ROOT = process.cwd()
const PARTNER_NETWORK = resolve(
  WEB_ROOT, '..', 'petcare_runtime', 'src', 'petcare', 'partner_network',
)

function mount(ui: React.ReactElement) {
  return render(<LangProvider>{ui}</LangProvider>)
}

function walk(dir: string, acc: string[] = []): string[] {
  let entries: string[]
  try { entries = readdirSync(dir) } catch { return acc }
  for (const e of entries) {
    if (e === 'node_modules' || e === '.next' || e.startsWith('.')) continue
    const p = join(dir, e)
    if (statSync(p).isDirectory()) walk(p, acc)
    else if (/\.(ts|tsx)$/.test(p)) acc.push(p)
  }
  return acc
}

const WEB_SOURCES = ['app', 'components', 'lib']
  .flatMap((d) => walk(join(WEB_ROOT, d)))

// ---------------------------------------------------------------------------
// CONSUME — every cited read resolves in the canonical tree
// ---------------------------------------------------------------------------

describe('PORT-09 the seam consumes the canonical services', () => {
  it('the canonical partner_network tree is where the seam says it is', () => {
    // Without this the citation checks below would skip silently and report a
    // clean seam because they resolved nothing.
    expect(existsSync(PARTNER_NETWORK), `partner_network not found at ${PARTNER_NETWORK}`).toBe(true)
  })

  it('every cited module exists in the canonical tree', () => {
    const missing = CANONICAL_READS
      .map((r) => r.module)
      .filter((m, i, a) => a.indexOf(m) === i)
      .filter((m) => !existsSync(join(PARTNER_NETWORK, `${m}.py`)))
    expect(missing, `cited modules absent from partner_network: ${missing}`).toEqual([])
  })

  it('every cited function is declared in the module that is cited', () => {
    const unresolved = CANONICAL_READS.filter((r) => {
      const file = join(PARTNER_NETWORK, `${r.module}.py`)
      if (!existsSync(file)) return true
      // Module-level `def name` or a method `    def name` both count as declared.
      return !new RegExp(`^\\s*def ${r.fn}\\b`, 'm').test(readFileSync(file, 'utf8'))
    })
    expect(
      unresolved.map((r) => `${r.module}.${r.fn}`),
      'seam cites reads that no longer exist in the canonical tree',
    ).toEqual([])
  })

  it('the citation matcher rejects a function that does not exist', () => {
    // Positive control. The check above passes by finding nothing wrong, which
    // is what a matcher that always returned true does too.
    const file = join(PARTNER_NETWORK, 'query.py')
    expect(/^\s*def get_verified_partners\b/m.test(readFileSync(file, 'utf8'))).toBe(true)
    expect(/^\s*def this_function_does_not_exist\b/m.test(readFileSync(file, 'utf8'))).toBe(false)
  })

  it('the citation set is not empty', () => {
    expect(CANONICAL_READS.length).toBeGreaterThanOrEqual(8)
    const surfaces = new Set(CANONICAL_READS.map((r) => `${r.module}.${r.fn}`))
    expect(surfaces.size).toBe(CANONICAL_READS.length)
  })
})

// ---------------------------------------------------------------------------
// NEVER RE-OWN — no marketplace logic anywhere in the web tree
// ---------------------------------------------------------------------------

describe('PORT-09 the web tree owns no marketplace logic', () => {
  it('has web sources to scan (the absence guard is not vacuous)', () => {
    expect(WEB_SOURCES.length).toBeGreaterThan(20)
  })

  it('does not reimplement a settlement or contract state machine', () => {
    /*
     * The canonical services own these transitions. A TypeScript copy would be
     * a second source of truth with no test binding it to the first.
     */
    const forbidden = [
      /\bSETTLEMENT_(STATES|TRANSITIONS)\b/,
      /\bCONTRACT_(STATES|TRANSITIONS)\b/,
      /\bcanTransition\s*\(/,
      /\bapproveSettlement\s*\(/,
      /\brejectSettlement\s*\(/,
    ]
    const offenders: string[] = []
    for (const file of WEB_SOURCES) {
      const text = readFileSync(file, 'utf8')
      for (const pattern of forbidden) {
        if (pattern.test(text)) offenders.push(`${file} :: ${pattern}`)
      }
    }
    expect(offenders, 'marketplace state logic re-owned in the web tree').toEqual([])
  })

  it('does not reimplement pricing, commission or settlement arithmetic', () => {
    const forbidden = [
      /\bcommission(Rate|Amount)\b/i,
      /\bcalculate(Price|Commission|Settlement|Payout)\b/i,
      /\bselectBestOffer\b/,
      /\bsortOffersLowToHigh\b/,
      /\bnetPayout\b/i,
    ]
    const offenders: string[] = []
    for (const file of WEB_SOURCES) {
      const text = readFileSync(file, 'utf8')
      for (const pattern of forbidden) {
        if (pattern.test(text)) offenders.push(`${file} :: ${pattern}`)
      }
    }
    expect(offenders, 'marketplace pricing logic re-owned in the web tree').toEqual([])
  })

  it('the re-ownership scanner would find those patterns if they were present', () => {
    // Positive control for the two guards above, against a synthetic source
    // rather than a real one, so proving the scanner works cannot itself
    // introduce the thing it forbids.
    const synthetic = 'export function calculateCommission(x: number) { return x * 0.1 }'
    expect(/\bcalculate(Price|Commission|Settlement|Payout)\b/i.test(synthetic)).toBe(true)
    expect(/\bcalculate(Price|Commission|Settlement|Payout)\b/i.test('const x = 1')).toBe(false)
  })

  it('the seam module carries citations only, not domain values', () => {
    // A price, rate or threshold literal in the seam is the first step of
    // re-owning. Version-like and index literals are not what this is about,
    // so it looks for decimal fractions and percentages specifically.
    const seam = readFileSync(join(WEB_ROOT, 'lib', 'marketplace.ts'), 'utf8')
    expect(seam).not.toMatch(/\b0\.\d+\b/)
    expect(seam).not.toMatch(/\b\d+\s*%/)
  })
})

// ---------------------------------------------------------------------------
// FAIL CLOSED — unwired means unwired, and it says so
// ---------------------------------------------------------------------------

describe('PORT-09 the seam fails closed', () => {
  it('is unwired, because activation is not authorized', () => {
    expect(MARKETPLACE_SEAM_WIRED).toBe(false)
  })

  it('returns a stated reason rather than an empty list', () => {
    // An empty list would be a claim about the domain — "the marketplace has no
    // partners" — that this surface is not entitled to make.
    const state = readMarketplace()
    expect(state.wired).toBe(false)
    expect(state).toHaveProperty('reason', 'NO_CANONICAL_TRANSPORT')
    expect(state).not.toHaveProperty('items')
  })

  it('attempts no network call while unwired', async () => {
    const spy = vi.spyOn(globalThis, 'fetch')
    mount(<MarketplaceSeamPanel />)
    expect(spy).not.toHaveBeenCalled()
    spy.mockRestore()
  })

  it('discloses on the panel that nothing is connected', () => {
    mount(<MarketplaceSeamPanel />)
    expect(screen.getByTestId('marketplace-seam-unwired')).toBeInTheDocument()
  })

  it('renders the citations it will consume and no partner rows', () => {
    mount(<MarketplaceSeamPanel />)
    const list = screen.getByTestId('marketplace-seam-citations')
    expect(list.querySelectorAll('li')).toHaveLength(CANONICAL_READS.length)
    expect(screen.queryAllByRole('row')).toHaveLength(0)
  })

  it('is mounted on /admin, which is where the plan targets it', () => {
    mount(<AdminPage />)
    expect(screen.getByTestId('marketplace-seam-panel')).toBeInTheDocument()
    expect(screen.getByTestId('marketplace-seam-unwired')).toBeInTheDocument()
  })
})
