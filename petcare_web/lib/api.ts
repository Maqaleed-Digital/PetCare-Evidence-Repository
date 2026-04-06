import { env } from '@/lib/env'

export async function apiHealth(): Promise<{ ok: boolean; status: number }> {
  const res = await fetch(`${env.NEXT_PUBLIC_API_BASE_URL.replace(/\/$/, '')}/health`, {
    cache: 'no-store'
  })
  return { ok: res.ok, status: res.status }
}
