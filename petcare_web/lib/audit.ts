import { env } from '@/lib/env'

export type AuditEvent = {
  event_name: string
  actor_role: string
  surface: string
  correlation_id: string
}

export async function emitAuditEvent(event: AuditEvent): Promise<{ ok: boolean; status: number }> {
  const res = await fetch(env.AUDIT_PROBE_ENDPOINT, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify(event),
    cache: 'no-store'
  })
  return { ok: res.ok, status: res.status }
}
