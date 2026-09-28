'use client'

/**
 * Account centre (MVC-EPC-D-001 Lane D, D2 — journeys J-O2 consent and J-O3 profile + export). Everything shown here is
 * read from the served app: the profile (/api/me/profile), the consent ledger (/api/me/consents, append-only on the
 * server) and the personal-data export (/api/me/export, SQ-3 #11 — the server demands step-up; the client only reacts).
 * Nothing is kept in browser storage.
 */

import { FormEvent, useCallback, useEffect, useState } from 'react'
import { Button, Card, Copy, DataView, Field, Notice, useCopy } from '@/components/ui'
import { useStepUp } from '@/components/StepUp'

const apiBase = (process.env.NEXT_PUBLIC_API_BASE_URL ?? '').replace(/\/$/, '')
const call = (path: string, init?: RequestInit) => fetch(`${apiBase}${path}`, {
  credentials: 'include', ...init, headers: { 'Content-Type': 'application/json', ...(init?.headers ?? {}) },
})

export const ACC = {
  profileTitle: { ar: 'الملف الشخصي', en: 'Profile' },
  name: { ar: 'الاسم الظاهر', en: 'Display name' },
  email: { ar: 'البريد الإلكتروني', en: 'Email' },
  save: { ar: 'حفظ', en: 'Save' },
  saved: { ar: 'تم حفظ الاسم.', en: 'Your name was saved.' },
  nameInvalid: { ar: 'أدخل اسماً من 1 إلى 120 حرفاً.', en: 'Enter a name of 1 to 120 characters.' },
  consentTitle: { ar: 'الموافقات', en: 'Consents' },
  consentIntro: { ar: 'اختياراتك محفوظة في حسابك، وكل تغيير يُسجَّل ولا يُحذف.', en: 'Your choices are stored on your account; every change is recorded and never erased.' },
  privacy_notice: { ar: 'إشعار الخصوصية (نظام حماية البيانات الشخصية)', en: 'Privacy notice (Saudi PDPL)' },
  care_reminders: { ar: 'تذكيرات رعاية حيواناتي الأليفة', en: 'Care reminders for my pets' },
  marketing_messages: { ar: 'أخبار المنتج والعروض', en: 'Product news and offers' },
  granted: { ar: 'موافَق عليه', en: 'Granted' },
  notGranted: { ar: 'غير موافَق عليه', en: 'Not granted' },
  grant: { ar: 'أوافق', en: 'Grant' },
  revoke: { ar: 'سحب الموافقة', en: 'Withdraw' },
  acknowledge: { ar: 'أقرّ بإشعار الخصوصية', en: 'Acknowledge the privacy notice' },
  notRevocable: { ar: 'لسحب هذه الموافقة يجب إغلاق الحساب عبر طلب الحذف أدناه.', en: 'To withdraw this, close your account through the erasure request below.' },
  history: { ar: 'سجل التغييرات', en: 'Change history' },
  GRANT: { ar: 'منح', en: 'Granted' },
  REVOKE: { ar: 'سحب', en: 'Withdrawn' },
  exportTitle: { ar: 'تنزيل بياناتي', en: 'Download my data' },
  exportIntro: { ar: 'ملف يحتوي بياناتك الشخصية وبيانات حيواناتك الأليفة وموافقاتك. يتطلب تأكيد الهوية.', en: 'A file with your personal data, your pets and your consents. Requires identity verification.' },
  exportCta: { ar: 'تنزيل الملف', en: 'Download file' },
  exportDone: { ar: 'تم تنزيل الملف.', en: 'Your file was downloaded.' },
  failed: { ar: 'تعذّر إكمال الطلب. حاول مرة أخرى.', en: 'That did not work. Try again.' },
} satisfies Record<string, Copy>

type Profile = { user_id: string; email: string; full_name: string; role: string }
type PurposeId = 'privacy_notice' | 'care_reminders' | 'marketing_messages'
type Purpose = { purpose: PurposeId; granted: boolean; since: string | null; revocable: boolean }
type Ledger = { purposes: Purpose[]; history: { event_id: string; purpose: PurposeId; action: 'GRANT' | 'REVOKE'; at: string }[] }
type Status = 'loading' | 'error' | 'ready'

function useResource<T>(path: string): [Status, T | null, () => void, (v: T) => void] {
  const [status, setStatus] = useState<Status>('loading')
  const [data, setData] = useState<T | null>(null)
  const load = useCallback(() => {
    setStatus('loading')
    call(path).then(r => (r.ok ? r.json() : Promise.reject(r.status)))
      .then(b => { setData(b); setStatus('ready') }).catch(() => setStatus('error'))
  }, [path])
  useEffect(load, [load])
  return [status, data, load, setData]
}

export function ProfileCard() {
  const { tr } = useCopy()
  const [status, profile, reload, setProfile] = useResource<Profile>('/api/me/profile')
  const [name, setName] = useState('')
  const [msg, setMsg] = useState<'none' | 'saved' | 'invalid' | 'failed'>('none')
  useEffect(() => { if (profile) setName(profile.full_name) }, [profile])

  async function save(e: FormEvent) {
    e.preventDefault()
    setMsg('none')
    const r = await call('/api/me/profile', { method: 'PUT', body: JSON.stringify({ full_name: name }) }).catch(() => null)
    if (r?.ok) {
      const b = await r.json()
      if (profile) setProfile({ ...profile, full_name: b.full_name })
      setMsg('saved')
    } else setMsg(r?.status === 400 ? 'invalid' : 'failed')
  }

  return (
    <Card title={ACC.profileTitle} testId="profile-card">
      <DataView status={status} data={profile} onRetry={reload}>
        {p => (
          <form onSubmit={save} className="ds-stack" data-testid="profile-form">
            <p className="ds-muted"><span>{tr(ACC.email)}: </span><bdi translate="no" data-testid="profile-email">{p.email}</bdi></p>
            <Field label={ACC.name} value={name} onChange={e => setName(e.currentTarget.value)} maxLength={120} required
              name="full_name" error={msg === 'invalid' ? tr(ACC.nameInvalid) : undefined} />
            <div><Button type="submit">{tr(ACC.save)}</Button></div>
            {msg === 'saved' && <Notice tone="success" testId="profile-saved">{tr(ACC.saved)}</Notice>}
            {msg === 'failed' && <Notice tone="danger">{tr(ACC.failed)}</Notice>}
          </form>
        )}
      </DataView>
    </Card>
  )
}

export function ConsentLedger() {
  const { tr, lang } = useCopy()
  const [status, ledger, reload, setLedger] = useResource<Ledger>('/api/me/consents')
  const [busy, setBusy] = useState<string | null>(null)
  const [failed, setFailed] = useState(false)

  async function change(purpose: PurposeId, action: 'GRANT' | 'REVOKE') {
    setBusy(purpose); setFailed(false)
    const r = await call(`/api/me/consents/${purpose}`, { method: 'POST', body: JSON.stringify({ action }) }).catch(() => null)
    if (r?.ok) setLedger(await r.json()); else setFailed(true)
    setBusy(null)
  }
  const when = (iso: string) => new Date(iso).toLocaleString(lang === 'ar' ? 'ar-SA' : 'en-GB',
    { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })

  return (
    <Card title={ACC.consentTitle} testId="consent-ledger">
      <p className="ds-muted">{tr(ACC.consentIntro)}</p>
      <DataView status={status} data={ledger} onRetry={reload}>
        {l => (
          <div className="ds-stack">
            <ul className="ds-list" aria-label={tr(ACC.consentTitle)}>
              {l.purposes.map(p => (
                <li key={p.purpose} className="ds-row ds-row--between" data-testid={`consent-${p.purpose}`}
                  data-granted={p.granted ? 'true' : 'false'}>
                  <span>
                    <strong>{tr(ACC[p.purpose])}</strong>{' '}
                    <span className={`ds-badge${p.granted ? ' ds-badge--success' : ''}`}>{tr(p.granted ? ACC.granted : ACC.notGranted)}</span>
                    {p.granted && !p.revocable && <span className="ds-hint" style={{ display: 'block' }}>{tr(ACC.notRevocable)}</span>}
                  </span>
                  {p.granted && p.revocable && (
                    <Button variant="secondary" disabled={busy === p.purpose} onClick={() => change(p.purpose, 'REVOKE')}
                      data-testid={`consent-${p.purpose}-revoke`}>{tr(ACC.revoke)}</Button>)}
                  {!p.granted && (
                    <Button disabled={busy === p.purpose} onClick={() => change(p.purpose, 'GRANT')}
                      data-testid={`consent-${p.purpose}-grant`}>{tr(p.revocable ? ACC.grant : ACC.acknowledge)}</Button>)}
                </li>
              ))}
            </ul>
            {failed && <Notice tone="danger">{tr(ACC.failed)}</Notice>}
            {l.history.length > 0 && (
              <details data-testid="consent-history">
                <summary>{tr(ACC.history)} ({l.history.length})</summary>
                <ol className="ds-list">
                  {l.history.map(h => (
                    <li key={h.event_id}>{tr(ACC[h.action])} · {tr(ACC[h.purpose])} · <time dateTime={h.at}>{when(h.at)}</time></li>
                  ))}
                </ol>
              </details>
            )}
          </div>
        )}
      </DataView>
    </Card>
  )
}

export function DataExportCard() {
  const { tr } = useCopy()
  const { stepUpFetch, stepUpUi } = useStepUp()
  const [msg, setMsg] = useState<'none' | 'done' | 'failed'>('none')

  async function download() {
    setMsg('none')
    const { response, state } = await stepUpFetch('/api/me/export', { method: 'GET' })
    if (state !== 'ok') return                                    // the step-up UI explains cancelled / enrol / failed
    if (!response.ok) { setMsg('failed'); return }
    const blob = await response.blob()
    const name = /filename="([^"]+)"/.exec(response.headers.get('content-disposition') ?? '')?.[1] ?? 'myveticare-personal-data.json'
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url; a.download = name; document.body.appendChild(a); a.click(); a.remove()
    URL.revokeObjectURL(url)
    setMsg('done')
  }

  return (
    <Card title={ACC.exportTitle} testId="data-export">
      <p className="ds-muted">{tr(ACC.exportIntro)}</p>
      <div><Button onClick={download} data-testid="data-export-download">{tr(ACC.exportCta)}</Button></div>
      {stepUpUi}
      {msg === 'done' && <Notice tone="success" testId="data-export-done">{tr(ACC.exportDone)}</Notice>}
      {msg === 'failed' && <Notice tone="danger">{tr(ACC.failed)}</Notice>}
    </Card>
  )
}
