/**
 * lib/featureFlags.ts — runtime gates for capabilities not yet activated.
 *
 * MVC-UX-WO-002 introduces FEATURE_AI as the gate for trust surfaces that
 * describe AI/agent output (ConfidenceBand, ExplainabilityPanel,
 * AuditTrailLink). Per the WO's honesty rules, these surfaces must be
 * embodied (built, wired, tested) but NEVER render while the engine
 * behind them is not running.
 *
 * Default: OFF. Opt-in via NEXT_PUBLIC_FEATURE_AI=true (build-time env).
 * `=== 'true'` is intentional — any other value (undefined, "false",
 * "1", etc.) leaves it OFF, so a typo cannot accidentally light up
 * AI surfaces in the pilot.
 */

export const FEATURE_AI: boolean =
  process.env.NEXT_PUBLIC_FEATURE_AI === 'true'

/**
 * A real audit-event handle. In the in-memory pilot this is always
 * null (no persistence → nothing to link to). When FEATURE_AI activates
 * and persistence comes online, the producer wires a real handle here
 * and AuditTrailLink lights up.
 */
export type AuditEventHandle = {
  audit_event_id: string
  occurred_at: string
} | null
