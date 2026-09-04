/**
 * PORT-09 — the marketplace seam.
 *
 * EP-07's marketplace is CANONICAL_ONLY and sealed (`ep07_seal_status:
 * PRESERVED`, commit 11f2a371). MVC-GOV-CANON-001 additionally lists
 * `marketplace_activation` under `does_not_authorize`. So this file is a seam
 * and not a client: it declares, in one place, exactly which canonical read
 * functions the admin surface will consume when an HTTP surface exists, and it
 * fails closed until then.
 *
 * The constraint from the port plan is "must consume, never re-own". Re-owning
 * is the easy mistake to make and the expensive one to unmake: a TypeScript
 * copy of a pricing rule or a settlement state machine becomes a second source
 * of truth that drifts silently from the sealed Python one, and nothing fails
 * when it does. Everything below is therefore names and shapes only. There is
 * no marketplace arithmetic, no ordering rule, no state transition, and no
 * eligibility decision in this file or anywhere in the web tree —
 * `__tests__/marketplace-seam.test.tsx` fails if one appears.
 *
 * The other half of "consume" is that the names must be real. Each entry below
 * cites a module and a function in
 * `petcare_runtime/src/petcare/partner_network/`, and the seam test resolves
 * every citation against that tree. A seam that named functions which did not
 * exist would look exactly like a wired one until the day it was wired.
 */

/** A canonical read the admin surface is entitled to consume. */
export interface CanonicalReadCitation {
  /** Module under petcare_runtime/src/petcare/partner_network/, without `.py`. */
  readonly module: string
  /** Function or method name declared in that module. */
  readonly fn: string
  /** What the admin surface would show with it. */
  readonly surface: string
}

export const CANONICAL_READS: readonly CanonicalReadCitation[] = [
  { module: 'query', fn: 'get_verified_partners', surface: 'partner directory' },
  { module: 'query', fn: 'get_pending_partners', surface: 'onboarding queue' },
  { module: 'catalog_query', fn: 'get_published_catalog_items', surface: 'published catalogue' },
  { module: 'catalog_query', fn: 'get_partner_catalog', surface: 'per-partner catalogue' },
  { module: 'contracts_query', fn: 'get_active_contracts', surface: 'contract register' },
  { module: 'contracts_query', fn: 'get_contract_breach_signals', surface: 'SLA breach signals' },
  { module: 'orders_query', fn: 'list_routed_orders', surface: 'routed orders' },
  { module: 'settlement_review_query', fn: 'list_in_queue', surface: 'settlement review queue' },
  { module: 'execution_visibility_query', fn: 'list_failed_events', surface: 'failed executions' },
] as const

/**
 * Whether a transport exists behind the seam.
 *
 * `petcare_api` exposes `/api/auth/*` and nothing else; there is no HTTP
 * surface over `partner_network`. Building one is marketplace activation, which
 * this repository's own authority does not authorize. The flag is therefore
 * false, and it is a constant rather than an environment variable on purpose —
 * an env var would let the seam be opened by configuration, outside the gate
 * that is supposed to open it.
 */
export const MARKETPLACE_SEAM_WIRED = false as const

export type SeamState =
  | { readonly wired: false; readonly reason: 'NO_CANONICAL_TRANSPORT' }
  | { readonly wired: true; readonly items: readonly unknown[] }

/**
 * Resolve the seam.
 *
 * Fails closed and says why. It does not return an empty list, because an empty
 * list is indistinguishable from "the marketplace has no partners" — which is a
 * claim about the domain this surface is not entitled to make.
 */
export function readMarketplace(): SeamState {
  if (!MARKETPLACE_SEAM_WIRED) {
    return { wired: false, reason: 'NO_CANONICAL_TRANSPORT' }
  }
  /* istanbul ignore next — unreachable until a transport is authorized. */
  throw new Error(
    'MARKETPLACE_SEAM_WIRED is true but no transport is implemented. ' +
    'Wiring it requires marketplace activation, which MVC-GOV-CANON-001 ' +
    'lists under does_not_authorize.',
  )
}
